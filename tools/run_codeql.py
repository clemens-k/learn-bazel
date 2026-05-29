#!/usr/bin/env python3
"""
run_codeql.py — Local CodeQL C/C++ analysis for Bazel projects.

Mirrors the phase structure of .github/workflows/codeql.yml so that local
runs are easy to compare with CI output:

  Phase 1: Initialize CodeQL    →  codeql database init
  Phase 2: Traced Build         →  codeql database trace-command  (×N targets)
  Phase 3: Finalize Database    →  codeql database finalize
  Phase 4: Run Queries          →  codeql database run-queries
  Phase 5: Interpret Results    →  codeql database interpret-results → SARIF
  Phase 6: Summary              →  baseline LOC  +  SARIF alert counts

All output is stored inside _codeql/ at the project root — no files are
written to external directories, making cleanup and debugging straightforward.

Usage examples
--------------
  # Analyse all targets in the current workspace (default)
  python3 tools/run_codeql.py

  # Analyse a specific target
  python3 tools/run_codeql.py //:my_app

  # Multiple targets
  python3 tools/run_codeql.py //:app_a //:app_b

  # Clean previous run first
  python3 tools/run_codeql.py --clean //...

  # Lighter query suite
  python3 tools/run_codeql.py --suites security-extended

  # Named Bazel config (defined in .bazelrc)
  python3 tools/run_codeql.py -c debug //...
  python3 tools/run_codeql.py -c release //...
  python3 tools/run_codeql.py -c debug -c asan //...

  # Pass arbitrary extra flags directly to bazel build (after --)
  python3 tools/run_codeql.py //... -- --jobs=4 --sandbox_debug

  # Combine: named config + extra flags
  python3 tools/run_codeql.py -c debug //... -- --jobs=4
"""

import argparse
import json
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Directory layout (all relative to project root)
# ---------------------------------------------------------------------------

_CODEQL_RELDIR = "_codeql"          # root output dir
_DB_SUBDIR = "db"                    # CodeQL database
_RESULTS_SUBDIR = "results"          # SARIF files
_LOGS_SUBDIR = "logs"                # per-phase log files
_SARIF_FILENAME = "cpp.sarif"


# ---------------------------------------------------------------------------
# Query suite aliases (short name → CodeQL pack reference)
# ---------------------------------------------------------------------------

QUERY_SUITES: dict[str, str] = {
    "security-extended":
        "codeql/cpp-queries:codeql-suites/cpp-security-extended.qls",
    "security-and-quality":
        "codeql/cpp-queries:codeql-suites/cpp-security-and-quality.qls",
    "code-scanning":
        "codeql/cpp-queries:codeql-suites/cpp-code-scanning.qls",
    "security-experimental":
        "codeql/cpp-queries:codeql-suites/cpp-security-experimental.qls",
}

DEFAULT_SUITES = "security-extended,security-and-quality"


# ---------------------------------------------------------------------------
# Output patterns to watch for
# ---------------------------------------------------------------------------

# CodeQL / general error indicators in command output
_ERROR_RES = [
    re.compile(r"^(error|Error|ERROR)\s*:", re.MULTILINE),
    re.compile(r"A fatal error occurred", re.IGNORECASE),
    re.compile(r"Extraction failed", re.IGNORECASE),
]

# CodeQL warning indicators
_WARN_RES = [
    re.compile(r"^(warning|Warning|WARNING)\s*:", re.MULTILINE),
]

# Bazel build-failure indicators
_BAZEL_FAILURE_RES = [
    re.compile(r"^Build FAILED", re.MULTILINE),
    re.compile(r"^ERROR: ", re.MULTILINE),
    re.compile(r"^FAILED: Build did not complete", re.MULTILINE),
]

# Bazel build-success indicators
_BAZEL_SUCCESS_RES = [
    re.compile(r"Build completed successfully"),
    re.compile(r"INFO: Build completed"),
]


# ---------------------------------------------------------------------------
# Terminal helpers  (##[group] / ##[warning] / ##[error] mirrors GitHub log)
# ---------------------------------------------------------------------------

def _color_supported() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ

_R = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_CYAN = "\033[36m"


def _c(text: str, *codes: str) -> str:
    return ("".join(codes) + text + _R) if _color_supported() else text


def phase_header(title: str) -> None:
    print()
    print(_c(f"##[group] {title}", _BOLD, _CYAN))


def phase_footer() -> None:
    print(_c("##[endgroup]", _DIM))


def log_info(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  [{ts}] {msg}")


def log_ok(msg: str) -> None:
    print(_c(f"  ✓ {msg}", _GREEN))


def log_warn(msg: str) -> None:
    print(_c(f"##[warning] {msg}", _YELLOW))


def log_err(msg: str) -> None:
    print(_c(f"##[error] {msg}", _RED, _BOLD), file=sys.stderr)


# ---------------------------------------------------------------------------
# Command execution
# ---------------------------------------------------------------------------

class _Result:
    """Return value of run_cmd."""
    def __init__(self, returncode: int, output: str) -> None:
        self.returncode = returncode
        self.output = output

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run_cmd(
    cmd: list,
    *,
    cwd: Path | None = None,
    log_file: Path | None = None,
) -> _Result:
    """
    Run *cmd*, stream output to stdout (indented), and optionally write a log.
    Merges stderr into stdout so both are captured together (same as the
    GitHub Actions runner which also merges them in the step log).
    Returns a _Result with the combined output.
    """
    cmd_strs = [str(c) for c in cmd]
    log_info("$ " + " ".join(cmd_strs))

    lines: list[str] = []
    log_fh = open(log_file, "w", encoding="utf-8") if log_file else None

    try:
        proc = subprocess.Popen(
            cmd_strs,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        for raw in proc.stdout:
            stripped = raw.rstrip("\n")
            print(f"    {stripped}")
            lines.append(stripped)
            if log_fh:
                log_fh.write(raw)
        proc.wait()
    finally:
        if log_fh:
            log_fh.close()

    return _Result(proc.returncode, "\n".join(lines))


def _find_errors(output: str) -> list[str]:
    found = []
    for pat in _ERROR_RES:
        found.extend(m.group(0).strip() for m in pat.finditer(output))
    return found


def _find_warnings(output: str) -> list[str]:
    found = []
    for pat in _WARN_RES:
        found.extend(m.group(0).strip() for m in pat.finditer(output))
    return found


def _bazel_failed(output: str) -> bool:
    return any(p.search(output) for p in _BAZEL_FAILURE_RES)


def _bazel_succeeded(output: str) -> bool:
    return any(p.search(output) for p in _BAZEL_SUCCESS_RES)


# ---------------------------------------------------------------------------
# Bazel spawn-strategy / .bazelrc helpers
# ---------------------------------------------------------------------------
#
# Why processwrapper-sandbox is required for CodeQL tracing
# ---------------------------------------------------------
# CodeQL traces C/C++ builds by injecting a shared library into compiler
# processes via LD_PRELOAD (set by `codeql database trace-command`).  Bazel
# runs compiler actions inside a sandbox whose type determines whether that
# environment variable reaches the compiler:
#
#   processwrapper-sandbox  – symlink-forest only, no Linux namespaces;
#                             child processes inherit the Bazel server's env.
#                             LD_PRELOAD reaches the compiler.  ✓
#
#   linux-sandbox            – uses CLONE_NEWNS / CLONE_NEWUSER namespaces;
#                             Bazel may reset the action env, stripping
#                             LD_PRELOAD before exec'ing the compiler.  ✗
#
# On GitHub Actions the Ubuntu runner VM cannot create new user namespaces,
# so Bazel automatically falls back to processwrapper-sandbox — which is why
# the workflow file needs no explicit spawn-strategy flag.
# Locally, linux-sandbox is often available, so we must pin the strategy.
#
# Precedence of .bazelrc files (lowest → highest, command line wins all):
#   /etc/bazel.bazelrc  →  ~/.bazelrc  →  <workspace>/.bazelrc  →  CLI flags

_SAFE_SPAWN_STRATEGY = "processwrapper-sandbox"

# Workspace-root marker files (same list Bazel uses internally)
_WORKSPACE_MARKERS = ("MODULE.bazel", "WORKSPACE.bazel", "WORKSPACE")

# Matches --spawn_strategy anywhere in a non-comment bazelrc line
_SPAWN_RE = re.compile(r"--spawn_strategy[=\s]+(\S+)")


def _find_workspace_root(start: Path) -> Path | None:
    """Walk up from *start* until a Bazel workspace-root marker is found."""
    p = start.resolve()
    while True:
        if any((p / m).exists() for m in _WORKSPACE_MARKERS):
            return p
        parent = p.parent
        if parent == p:
            return None
        p = parent


def _collect_bazelrc_files(build_cwd: Path) -> list[tuple[str, Path]]:
    """
    Return (label, path) pairs for the .bazelrc files Bazel would read,
    ordered by increasing precedence (last entry wins on conflicts).
    """
    candidates: list[tuple[str, Path]] = []

    sys_rc = Path("/etc/bazel.bazelrc")
    if sys_rc.exists():
        candidates.append(("system  ", sys_rc))

    user_rc = Path.home() / ".bazelrc"
    if user_rc.exists():
        candidates.append(("user    ", user_rc))

    ws_root = _find_workspace_root(build_cwd)
    if ws_root:
        ws_rc = ws_root / ".bazelrc"
        if ws_rc.exists():
            candidates.append(("workspace", ws_rc))

    return candidates


def _scan_bazelrc_spawn_strategy(
    rc_files: list[tuple[str, Path]]
) -> list[tuple[str, Path, int, str]]:
    """
    Scan bazelrc files for spawn_strategy settings.
    Returns list of (label, file, lineno, raw_line) for every match.
    """
    hits: list[tuple[str, Path, int, str]] = []
    for label, rc_path in rc_files:
        try:
            with open(rc_path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    if _SPAWN_RE.search(stripped):
                        hits.append((label, rc_path, lineno, stripped))
        except OSError:
            pass
    return hits


# ---------------------------------------------------------------------------
# System helpers
# ---------------------------------------------------------------------------

def _cpu_count() -> int:
    return multiprocessing.cpu_count()


def _ram_mb() -> int:
    """Return ~80 % of total RAM, capped at 32 GB, defaulting to 4 GB."""
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return min(int(kb / 1024 * 0.8), 32 * 1024)
    except OSError:
        pass
    return 4096


# ---------------------------------------------------------------------------
# Phase 1 — Initialize CodeQL database
# ---------------------------------------------------------------------------

def phase_init(db_dir: Path, source_root: Path, language: str, log_dir: Path) -> bool:
    """
    Mirrors: github/codeql-action/init
    Creates the skeleton CodeQL database and activates the tracing environment
    for subsequent trace-command calls.
    """
    phase_header("Initialize CodeQL")

    if db_dir.exists():
        log_info(f"Removing existing database: {db_dir}")
        shutil.rmtree(db_dir)

    cmd = [
        "codeql", "database", "init",
        db_dir,
        f"--language={language}",
        f"--source-root={source_root}",
        # Enables per-sublanguage file-coverage tracking (C vs C++),
        # matching the GitHub Actions --sublanguage-file-coverage flag.
        "--sublanguage-file-coverage",
    ]

    result = run_cmd(cmd, cwd=source_root, log_file=log_dir / "01-init.log")

    if not result.ok:
        log_err(f"codeql database init failed (exit {result.returncode})")
        for e in _find_errors(result.output)[:5]:
            log_err(e)
        phase_footer()
        return False

    for w in _find_warnings(result.output):
        log_warn(w)

    log_ok(f"Database initialised at {db_dir}")
    phase_footer()
    return True


# ---------------------------------------------------------------------------
# Phase 2 — Traced build
# ---------------------------------------------------------------------------

def phase_traced_build(
    db_dir: Path,
    targets: list[str],
    build_cwd: Path,
    extra_bazel_args: list[str],
    log_dir: Path,
) -> bool:
    """
    Mirrors: Run manual build steps
    Each Bazel target is built under codeql database trace-command so that
    the CodeQL C/C++ extractor can intercept compiler invocations via
    LD_PRELOAD and emit TRAP files.

    Spawn-strategy injection
    ------------------------
    --spawn_strategy=processwrapper-sandbox is always injected so that Bazel
    passes the LD_PRELOAD set by trace-command through to compiler child
    processes.  Command-line flags take highest precedence in Bazel, so this
    overrides any spawn_strategy already set in .bazelrc files.
    User-supplied --bazel-flags come after the injection and can override it
    if a specific strategy (e.g. 'local') is preferred instead.
    """
    phase_header("Traced Build")

    # --- Inspect .bazelrc files for spawn_strategy ---
    rc_files = _collect_bazelrc_files(build_cwd)
    log_info(
        "Bazelrc files (lowest → highest precedence; CLI flags override all):"
    )
    if rc_files:
        for label, rc_path in rc_files:
            log_info(f"  [{label}] {rc_path}")
    else:
        log_info("  (none found)")

    hits = _scan_bazelrc_spawn_strategy(rc_files)
    if hits:
        log_info("spawn_strategy entries found in .bazelrc (will be overridden):")
        for label, rc_path, lineno, raw in hits:
            effective = _SPAWN_RE.search(raw)
            value = effective.group(1) if effective else "?"
            log_info(f"  [{label}] {rc_path}:{lineno}  →  {raw}")
            if value not in (_SAFE_SPAWN_STRATEGY, "local"):
                log_warn(
                    f"[{label}] .bazelrc sets spawn_strategy={value}, which may "
                    f"block CodeQL LD_PRELOAD tracing. "
                    f"Overriding with --spawn_strategy={_SAFE_SPAWN_STRATEGY}."
                )
    else:
        log_info("  (no spawn_strategy entries found in .bazelrc)")

    # Always inject the safe strategy (command line > .bazelrc).
    # User --bazel-flags come after and can further override if needed.
    injected = [f"--spawn_strategy={_SAFE_SPAWN_STRATEGY}"]
    log_info(
        f"Injecting --spawn_strategy={_SAFE_SPAWN_STRATEGY} "
        "(mirrors GitHub Actions runner; ensures LD_PRELOAD reaches compiler)."
    )

    # Run `bazel clean` so that all C/C++ actions execute from scratch.
    # CodeQL tracing works by intercepting compiler invocations via LD_PRELOAD;
    # if Bazel serves the build from its action cache, no compiler runs and no
    # TRAP files are generated.  GitHub Actions is always a fresh environment,
    # which is why this step is not needed there.
    log_info("Running 'bazel clean' to force recompilation of all targets.")
    clean_result = run_cmd(
        ["bazel", "clean"],
        cwd=build_cwd,
        log_file=log_dir / "02-bazel-clean.log",
    )
    if not clean_result.ok:
        log_warn(
            f"'bazel clean' exited with code {clean_result.returncode}. "
            "Proceeding — cached actions may not be traced."
        )

    # Shut down any existing Bazel server so that the next build (inside
    # trace-command) starts a FRESH server process.  The fresh server inherits
    # the environment that trace-command has already set up — including the
    # LD_PRELOAD path to the CodeQL trace library — so every compiler child
    # process will be intercepted and produce TRAP files.
    #
    # Without this step, an already-running server (started before
    # trace-command set LD_PRELOAD) continues to be used and the compiler
    # runs, but without the tracer library, so no TRAP files are written.
    #
    # On GitHub Actions there is never a pre-existing server, so this is not
    # needed there.
    log_info("Running 'bazel shutdown' to restart the server with CodeQL LD_PRELOAD.")
    shutdown_result = run_cmd(
        ["bazel", "shutdown"],
        cwd=build_cwd,
        log_file=log_dir / "02-bazel-shutdown.log",
    )
    if not shutdown_result.ok:
        log_warn(
            f"'bazel shutdown' exited with code {shutdown_result.returncode}. "
            "Proceeding — tracing may fail if an existing server is reused."
        )

    for idx, target in enumerate(targets):
        log_info(f"Target [{idx + 1}/{len(targets)}]: {target}  (cwd: {build_cwd})")

        bazel_cmd = ["bazel", "build"] + injected + extra_bazel_args + [target]
        cmd = ["codeql", "database", "trace-command", db_dir, "--"] + bazel_cmd

        result = run_cmd(
            cmd,
            cwd=build_cwd,
            log_file=log_dir / f"02-build-{idx:02d}.log",
        )

        # Non-zero exit is a hard failure
        if not result.ok:
            log_err(
                f"trace-command for target '{target}' failed "
                f"(exit {result.returncode})"
            )
            if _bazel_failed(result.output):
                log_err("Bazel reported a build failure — see log for details.")
            phase_footer()
            return False

        # Zero exit but Bazel failure patterns in output → warn, do not abort
        if _bazel_failed(result.output):
            log_warn(
                f"Exit code 0 but Bazel failure patterns found for '{target}'. "
                "Extraction may be incomplete."
            )

        for w in _find_warnings(result.output):
            log_warn(w)

        if _bazel_succeeded(result.output):
            log_ok(f"Target {target}: build completed successfully")
        else:
            log_warn(
                f"Target {target}: could not confirm successful build in output. "
                "Extraction may be incomplete."
            )

    phase_footer()
    return True


# ---------------------------------------------------------------------------
# Phase 3 — Finalize database (TRAP import)
# ---------------------------------------------------------------------------

def phase_finalize(
    db_dir: Path,
    threads: int,
    ram: int,
    log_dir: Path,
) -> bool:
    """
    Mirrors: ##[group]Finalizing cpp  (part of github/codeql-action/analyze)
    Imports accumulated TRAP files and writes the queryable CodeQL database.
    """
    phase_header("Finalize Database")

    cmd = [
        "codeql", "database", "finalize",
        f"--threads={threads}",
        f"--ram={ram}",
        db_dir,
    ]

    result = run_cmd(cmd, log_file=log_dir / "03-finalize.log")

    if not result.ok:
        log_err(f"codeql database finalize failed (exit {result.returncode})")
        for e in _find_errors(result.output)[:5]:
            log_err(e)
        phase_footer()
        return False

    # Confirm TRAP import
    if "TRAP import complete" in result.output:
        m = re.search(r"TRAP import complete \((.+?)\)", result.output)
        log_ok("TRAP import complete" + (f" ({m.group(1)})" if m else ""))
    else:
        log_warn(
            "Could not find 'TRAP import complete' in finalize output. "
            "The database may be incomplete."
        )

    m = re.search(r"Finished writing database \((.+?)\)", result.output)
    if m:
        log_ok(f"Database written: {m.group(1)}")

    for w in _find_warnings(result.output):
        log_warn(w)

    phase_footer()
    return True


# ---------------------------------------------------------------------------
# Phase 4 — Run queries
# ---------------------------------------------------------------------------

def phase_run_queries(
    db_dir: Path,
    suite_names: list[str],
    threads: int,
    ram: int,
    log_dir: Path,
) -> tuple[bool, list[str]]:
    """
    Mirrors: ##[group]Running queries for cpp  (codeql database run-queries)
    Returns (success, resolved_suite_paths) so phase 5 can use the same refs.
    """
    phase_header("Run Queries")

    resolved: list[str] = []
    for name in suite_names:
        path = QUERY_SUITES.get(name, name)   # fall through if already a path
        resolved.append(path)
        log_info(f"Suite: {name}  →  {path}")

    cmd = [
        "codeql", "database", "run-queries",
        f"--threads={threads}",
        f"--ram={ram}",
        "--expect-discarded-cache",
        "--min-disk-free=1024",
        "-v",
        db_dir,
    ] + resolved

    result = run_cmd(cmd, log_file=log_dir / "04-run-queries.log")

    if not result.ok:
        log_err(f"codeql database run-queries failed (exit {result.returncode})")
        for e in _find_errors(result.output)[:5]:
            log_err(e)
        phase_footer()
        return False, resolved

    # Report query count
    loaded = re.findall(r"\[(\d+)/(\d+)\] Loaded", result.output)
    if loaded:
        log_ok(f"Loaded and executed {loaded[-1][1]} queries")

    for w in _find_warnings(result.output):
        log_warn(w)

    phase_footer()
    return True, resolved


# ---------------------------------------------------------------------------
# Phase 5 — Interpret results → SARIF
# ---------------------------------------------------------------------------

# Matches the coverage line produced by --sublanguage-file-coverage, e.g.:
#   "CodeQL scanned 3 out of 3 C files and 2 out of 2 C++ files ..."
#   "CodeQL scanned 1 out of 1 C files ..."
_SCANNED_RE = re.compile(r"CodeQL scanned \d+ out of \d+.*?files.*", re.IGNORECASE)


def phase_interpret_results(
    db_dir: Path,
    resolved_suites: list[str],
    sarif_file: Path,
    log_dir: Path,
) -> tuple[bool, str | None]:
    """
    Mirrors: Exporting results to SARIF  (codeql database interpret-results)
    Converts raw BQRS query results into the SARIF format consumed by
    GitHub Code Scanning and other alert viewers.

    Returns (success, scanned_line) where scanned_line is the
    "CodeQL scanned X out of Y files" coverage message if emitted.
    """
    phase_header("Interpret Results → SARIF")

    sarif_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "codeql", "database", "interpret-results",
        "--format=sarif-latest",
        f"--output={sarif_file}",
        "-v",
        # Per-sublanguage file-coverage tracking (mirrors GH Actions):
        # produces "CodeQL scanned X out of Y C files and Z out of W C++ files"
        "--sublanguage-file-coverage",
        # Diagnostics and metrics summaries (mirrors GH Actions):
        "--print-diagnostics-summary",
        "--print-metrics-summary",
        # SARIF quality improvements (both available in 2.24.1+):
        "--sarif-group-rules-by-pack",
        "--sarif-include-query-help=always",
        db_dir,
    ] + resolved_suites

    result = run_cmd(cmd, log_file=log_dir / "05-interpret.log")

    if not result.ok:
        log_err(
            f"codeql database interpret-results failed (exit {result.returncode})"
        )
        for e in _find_errors(result.output)[:5]:
            log_err(e)
        phase_footer()
        return False, None

    if not sarif_file.exists():
        log_err(f"SARIF file was not created at {sarif_file}")
        phase_footer()
        return False, None

    size_kb = sarif_file.stat().st_size / 1024
    log_ok(f"SARIF written: {sarif_file}  ({size_kb:.1f} KiB)")

    # Extract the "CodeQL scanned X out of Y files" line for the summary.
    scanned_line: str | None = None
    for line in result.output.splitlines():
        m = _SCANNED_RE.search(line)
        if m:
            scanned_line = m.group(0)
            break

    for w in _find_warnings(result.output):
        log_warn(w)

    phase_footer()
    return True, scanned_line


# ---------------------------------------------------------------------------
# Phase 6 — Summary
# ---------------------------------------------------------------------------

def phase_summary(
    db_dir: Path,
    sarif_file: Path,
    codeql_dir: Path,
    log_dir: Path,
    scanned_line: str | None = None,
) -> None:
    """
    Mirrors: "CodeQL scanned N out of N C files and N out of N C++ files"
    Prints:
      \u2022 File coverage line from interpret-results --sublanguage-file-coverage
      \u2022 Source baseline (LOC) from codeql database print-baseline
      \u2022 Alert counts parsed from the SARIF file
      \u2022 Paths to all output artefacts
    """
    phase_header("Summary")

    # --- Scanned-files coverage (mirrors the GH Actions summary line) ---
    if scanned_line:
        log_ok(scanned_line)

    # --- Source coverage / baseline ---
    log_info("Source file baseline (codeql database print-baseline):")
    bl_result = run_cmd(
        ["codeql", "database", "print-baseline", db_dir],
        log_file=log_dir / "06-baseline.log",
    )
    if bl_result.ok:
        for line in bl_result.output.splitlines():
            stripped = line.strip()
            if stripped:
                log_info(f"  {stripped}")
    else:
        log_warn(
            f"print-baseline failed (exit {bl_result.returncode}). "
            "Coverage information unavailable."
        )

    # --- Alert counts from SARIF ---
    print()
    log_info("Alert summary (parsed from SARIF):")
    if sarif_file.exists():
        try:
            with open(sarif_file, encoding="utf-8") as f:
                sarif = json.load(f)

            total = 0
            by_level: dict[str, int] = {}
            rules: set[str] = set()

            for run in sarif.get("runs", []):
                for r in run.get("results", []):
                    total += 1
                    level = r.get("level", "none")
                    by_level[level] = by_level.get(level, 0) + 1
                    rules.add(r.get("ruleId", "unknown"))

            log_ok(f"Total alerts: {total}")
            for level, count in sorted(by_level.items()):
                log_info(f"  {level:12s}: {count}")

            if rules:
                log_info(f"  Rules triggered ({len(rules)}):")
                for rule in sorted(rules)[:15]:
                    log_info(f"    - {rule}")
                if len(rules) > 15:
                    log_info(f"    ... and {len(rules) - 15} more")

        except (json.JSONDecodeError, KeyError, OSError) as exc:
            log_warn(f"Could not parse SARIF: {exc}")
    else:
        log_warn(f"SARIF file not found at {sarif_file}")

    # --- Artefact locations ---
    print()
    log_ok("Analysis complete.")
    log_info(f"  Output directory : {codeql_dir}")
    log_info(f"  CodeQL database  : {db_dir}")
    log_info(f"  SARIF results    : {sarif_file}")
    log_info(f"  Phase logs       : {log_dir}/")

    phase_footer()


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_codeql.py",
        description=__doc__.splitlines()[1].strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(__doc__.splitlines()[35:]),
    )

    p.add_argument(
        "targets",
        nargs="*",
        default=["//..."],
        metavar="TARGET",
        help="Bazel target(s) to build and analyse (default: //...)",
    )
    p.add_argument(
        "--build-cwd",
        default=None,
        metavar="DIR",
        help="Working directory for bazel build (default: project root)",
    )
    p.add_argument(
        "--suites",
        default=DEFAULT_SUITES,
        metavar="SUITE[,SUITE...]",
        help=(
            "Comma-separated CodeQL query suites. "
            f"Available aliases: {', '.join(QUERY_SUITES)}. "
            f"Default: {DEFAULT_SUITES}"
        ),
    )
    p.add_argument(
        "--language",
        default="cpp",
        metavar="LANG",
        help="CodeQL language extractor to use (default: cpp)",
    )
    p.add_argument(
        "-s", "--source-root",
        default=None,
        metavar="DIR",
        help="Source root for the CodeQL database (default: project root)",
    )
    p.add_argument(
        "-j", "--threads",
        type=int,
        default=None,
        metavar="N",
        help="Threads for analysis (default: CPU count)",
    )
    p.add_argument(
        "--ram",
        type=int,
        default=None,
        metavar="MB",
        help="RAM limit in MB (default: 80 %% of system RAM)",
    )
    p.add_argument(
        "-c", "--config",
        action="append",
        default=[],
        metavar="NAME",
        dest="configs",
        help=(
            "Bazel named config to apply (may be repeated: -c debug -c asan). "
            "Expands to --config=<NAME> in every 'bazel build' invocation. "
            "Configs must be defined in a .bazelrc file."
        ),
    )
    p.add_argument(
        "--bazel-flags",
        default="",
        metavar="FLAGS",
        help=(
            "Extra flags passed verbatim to every 'bazel build' invocation. "
            "Prefer '-c NAME' for named configs or the '-- <flags>' separator "
            "for ad-hoc flags."
        ),
    )
    p.add_argument(
        "--clean",
        action="store_true",
        help=f"Remove the entire {_CODEQL_RELDIR}/ directory before starting",
    )

    return p


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Split argv at '--': everything after the separator is passed verbatim to
    # every 'bazel build' invocation, avoiding argparse's leading-dash ambiguity.
    import sys as _sys
    _argv = _sys.argv[1:]
    try:
        _sep = _argv.index("--")
        _passthrough = _argv[_sep + 1 :]
        _argv = _argv[:_sep]
    except ValueError:
        _passthrough = []

    args = _build_parser().parse_args(_argv)

    # Resolve project root (parent of the tools/ directory containing this script)
    project_root = Path(__file__).resolve().parent.parent

    codeql_dir  = project_root / _CODEQL_RELDIR
    db_dir      = codeql_dir / _DB_SUBDIR
    results_dir = codeql_dir / _RESULTS_SUBDIR
    logs_dir    = codeql_dir / _LOGS_SUBDIR
    sarif_file  = results_dir / _SARIF_FILENAME

    source_root = Path(args.source_root).resolve() if args.source_root else project_root
    # If --build-cwd is not set, default to --source-root (when given) so that
    # `-s examples/foo/` targets that workspace for both analysis and building.
    build_cwd   = (
        Path(args.build_cwd).resolve()   if args.build_cwd
        else source_root                 if args.source_root
        else project_root
    )

    threads = args.threads or _cpu_count()
    ram     = args.ram     or _ram_mb()
    suites  = [s.strip() for s in args.suites.split(",") if s.strip()]
    extra_bazel_args = (
        [f"--config={c}" for c in args.configs]
        + (args.bazel_flags.split() if args.bazel_flags else [])
        + _passthrough
    )

    # ---- Prerequisites ----
    for tool in ("codeql", "bazel"):
        if shutil.which(tool) is None:
            log_err(f"'{tool}' not found in PATH. Please install it first.")
            sys.exit(1)

    # ---- Header ----
    print(_c("=" * 62, _BOLD, _CYAN))
    print(_c("  CodeQL C/C++ Analysis — Bazel project", _BOLD, _CYAN))
    print(_c("=" * 62, _BOLD, _CYAN))
    log_info(f"Date/time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_info(f"Project root : {project_root}")
    log_info(f"Source root  : {source_root}")
    log_info(f"Build cwd    : {build_cwd}")
    log_info(f"Targets      : {', '.join(args.targets)}")
    log_info(f"Suites       : {', '.join(suites)}")
    log_info(f"Threads      : {threads}")
    log_info(f"RAM          : {ram} MB")
    log_info(f"Output dir   : {codeql_dir}")

    # ---- Clean ----
    if args.clean and codeql_dir.exists():
        log_info(f"--clean: removing {codeql_dir}")
        shutil.rmtree(codeql_dir)

    # ---- Create output dirs ----
    logs_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    # ---- Phases ----
    if not phase_init(db_dir, source_root, args.language, logs_dir):
        sys.exit(2)

    if not phase_traced_build(db_dir, args.targets, build_cwd, extra_bazel_args, logs_dir):
        sys.exit(3)

    if not phase_finalize(db_dir, threads, ram, logs_dir):
        sys.exit(4)

    ok, resolved_suites = phase_run_queries(db_dir, suites, threads, ram, logs_dir)
    if not ok:
        sys.exit(5)

    ok_interp, scanned_line = phase_interpret_results(db_dir, resolved_suites, sarif_file, logs_dir)
    if not ok_interp:
        sys.exit(6)

    phase_summary(db_dir, sarif_file, codeql_dir, logs_dir, scanned_line)


if __name__ == "__main__":
    main()
