# run_codeql.py — Developer Guide

Local CodeQL C/C++ analysis for Bazel projects, mirroring the phase
structure of `.github/workflows/codeql.yml` so that local runs are directly
comparable to CI output.

---

## Quick start

```bash
# Analyse a self-contained Bazel workspace under examples/configs/
python3 tools/run_codeql.py -s examples/configs/ --clean //...

# With a named .bazelrc config
python3 tools/run_codeql.py -s examples/configs/ --clean -c debug //...

# Pass arbitrary extra flags to bazel build (after --)
python3 tools/run_codeql.py -s examples/configs/ --clean //... -- --jobs=4
```

All output lands in `_codeql/` at the repository root (database, SARIF,
per-phase log files).

---

## High-level overview

CodeQL for C/C++ works through **compilation tracing**: the tool
intercepts every compiler invocation during the real build, observes its
inputs, and writes intermediate `.trap` files encoding the program's abstract
syntax tree.  Only after the full build completes does CodeQL import the trap
files and run queries against them.

```
Source code
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Phase 1 – Init          codeql database init                           │
│  Create the database skeleton and activate the tracer environment.      │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Phase 2 – Traced Build   codeql database trace-command … bazel build   │
│  Run the real Bazel build inside the CodeQL tracer.  Every compiler     │
│  invocation is intercepted via LD_PRELOAD; one .trap file per TU.       │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Phase 3 – Finalize       codeql database finalize                      │
│  Import all .trap files and produce the queryable CodeQL DB.            │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Phase 4 – Run Queries    codeql database run-queries                   │
│  Execute the selected query suites against the database.                │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Phase 5 – Interpret      codeql database interpret-results             │
│  Convert raw BQRS result files to SARIF for alert viewers / upload.     │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Phase 6 – Summary        codeql database print-baseline + SARIF parse  │
│  Report file coverage, alert counts, and output paths.                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase-by-phase breakdown

Each section lists the exact shell command the script constructs, followed by
an argument reference.  Arguments are classified as:

- **[crucial]** — omitting or changing this breaks the analysis or produces
  incorrect results.
- **[convenience]** — mirrors GitHub Actions behaviour, improves diagnostics,
  or provides UX polish; the analysis technically completes without it.

---

### Phase 1 — Initialize CodeQL database

```bash
codeql database init \
    <db_dir>                         \
    --language=cpp                   \
    --source-root=<source_root>      \
    --sublanguage-file-coverage
```

| Argument | Class | Explanation |
|---|---|---|
| `<db_dir>` | **crucial** | Path where the database skeleton will be created.  Must not already exist (the script removes an old database automatically when `--clean` is given). |
| `--language=cpp` | **crucial** | Selects the C/C++ extractor.  CodeQL's extractor family is language-specific; the `cpp` extractor handles both C and C++. |
| `--source-root=<path>` | **crucial** | Root of the source tree to analyse.  All source file paths in the final database are expressed relative to this directory.  It also determines which files count toward the baseline ("lines of code") and the file-coverage report.  Must match the directory that contains the Bazel workspace files. |
| `--sublanguage-file-coverage` | convenience | Enables independent tracking of C files and C++ files.  Without it, both are reported together as "C/C++ files".  This flag is required by the GitHub Actions `codeql-action` and produces the summary line _"CodeQL scanned N out of N C files and M out of M C++ files"_. |

**What happens internally:** CodeQL creates a skeleton database directory
containing metadata, activates the extraction tracer, and pre-computes a
source-file baseline used later for coverage reporting.

---

### Phase 2 — Traced build

This phase runs two Bazel preparation steps and then the actual traced build.

#### 2a — Bazel clean  *(local only)*

```bash
bazel clean
```

Forces Bazel to discard its action cache so that every C/C++ compilation
action executes from scratch.  **This step does not exist in GitHub Actions**
because each CI run starts in a fresh environment with no pre-existing cache.

Locally, if a previous successful build has been cached, Bazel will not
re-invoke the compiler — it will serve outputs from cache — and CodeQL will
never intercept those compiler calls, resulting in zero TRAP files and a
"no source code seen" error from the Finalize phase.

#### 2b — Bazel shutdown  *(local only)*

```bash
bazel shutdown
```

Kills the running Bazel server so that the _next_ `bazel build` (inside
`trace-command`) starts a fresh server process.  **This step does not exist
in GitHub Actions** for the same reason — there is no pre-existing server.

The reason this matters is subtle and worth understanding in detail:

> `codeql database trace-command` works by setting `LD_PRELOAD` in the
> environment of the shell process that launches the build command.  Any
> Bazel server that was already running before `trace-command` was called
> does **not** have `LD_PRELOAD` in its environment, because it was started
> earlier when the environment was clean.  When that old server spawns
> compiler child processes, those children inherit the server's (un-patched)
> environment — not the one `trace-command` set up — so the CodeQL tracer
> library is never loaded and no TRAP files are written.
>
> By shutting down the server first, the subsequent `bazel build` must start
> a new server.  That new server is spawned inside the environment
> `trace-command` has already configured, so it — and all compiler children
> it spawns — inherit `LD_PRELOAD`, and tracing works correctly.

#### 2c — Traced build proper

```bash
codeql database trace-command <db_dir> \
    -- \
    bazel build \
        --spawn_strategy=processwrapper-sandbox \
        [--config=<name>] \
        [<extra_bazel_flags>] \
        <target>
```

| Argument | Class | Explanation |
|---|---|---|
| `<db_dir>` | **crucial** | The database initialized in Phase 1.  CodeQL writes TRAP files into this directory as it traces each compiler call. |
| `--` | **crucial** | Separator between CodeQL's own arguments and the build command.  Everything after `--` is the command CodeQL will run under its tracer. |
| `bazel build` | **crucial** | The actual build tool invocation.  Could be any build command (make, cmake, ninja), but must invoke a C/C++ compiler. |
| `--spawn_strategy=processwrapper-sandbox` | **crucial (locally)** | See the Bazel-specific section below.  This is **not needed** on GitHub Actions runners because linux-sandbox namespaces are unavailable there and Bazel falls back automatically. |
| `--config=<name>` | convenience | Applies a named Bazel configuration defined in a `.bazelrc` file.  Useful when builds differ meaningfully between configurations (debug symbols, sanitizers, optimization level). |
| `<extra_bazel_flags>` | convenience | Any additional flags forwarded from `--bazel-flags` or after `--` on the `run_codeql.py` command line. |
| `<target>` | **crucial** | The Bazel target(s) to build.  `//...` builds all targets in the workspace; specific targets like `//:my_app` can narrow the scope. |

---

### Phase 3 — Finalize database (TRAP import)

```bash
codeql database finalize \
    --threads=<N>   \
    --ram=<MB>      \
    <db_dir>
```

| Argument | Class | Explanation |
|---|---|---|
| `<db_dir>` | **crucial** | The database directory containing accumulated TRAP files from Phase 2.  After this phase the database is sealed and queryable. |
| `--threads=N` | convenience | Parallelises TRAP import.  Defaults to the machine's CPU count.  More threads = faster import on large codebases. |
| `--ram=MB` | convenience | Memory cap for the import process.  The script defaults to 80% of available RAM, matching the GitHub Actions convention. |

**What "TRAP import" means:** Each compiler invocation in Phase 2 produced a
`.trap` file (Textual Relation Architecture Protocol) — a flat, relational
representation of the source file's AST and type information.  Finalize reads
all those files, validates them, and writes the compact database format that
CodeQL queries operate on.  A successful import prints
`TRAP import complete (Xms)`.

If this phase emits *"could not process any of it"*, it almost always means
no TRAP files were created — i.e. Phase 2 ran but no compiler was invoked.
The two most common local causes are a warm Bazel action cache (fixed by
`bazel clean`) or a pre-existing Bazel server (fixed by `bazel shutdown`).

---

### Phase 4 — Run queries

```bash
codeql database run-queries \
    --threads=<N>              \
    --ram=<MB>                 \
    --expect-discarded-cache   \
    --min-disk-free=1024       \
    -v                         \
    <db_dir>                   \
    <suite1> [<suite2> ...]
```

| Argument | Class | Explanation |
|---|---|---|
| `<db_dir>` | **crucial** | Sealed database from Phase 3. |
| `<suite>` | **crucial** | One or more query suite paths (`.qls` files) or pack references.  The script accepts short aliases: `security-extended`, `security-and-quality`, `code-scanning`, `security-experimental`. |
| `--threads=N` | convenience | Parallel query evaluation threads. |
| `--ram=MB` | convenience | Memory cap for the evaluator. |
| `--expect-discarded-cache` | convenience | Suppresses a warning that CodeQL emits when it detects a query cache has been invalidated (e.g. after switching database versions).  Has no effect on results. |
| `--min-disk-free=1024` | convenience | Safety guardrail: abort if fewer than 1 GiB of disk remains.  Prevents filling the disk during large analysis runs. |
| `-v` | convenience | Verbose output, including `[N/M] Loaded …` progress lines that the script parses to report how many queries were executed. |

**Default suites:** The script runs `security-extended` and
`security-and-quality` by default — the same two suites the GitHub Actions
workflow uses when `queries: security-and-quality` is set.

---

### Phase 5 — Interpret results → SARIF

```bash
codeql database interpret-results \
    --format=sarif-latest              \
    --output=<sarif_file>              \
    -v                                 \
    --sublanguage-file-coverage        \
    --print-diagnostics-summary        \
    --print-metrics-summary            \
    --sarif-group-rules-by-pack        \
    --sarif-include-query-help=always  \
    <db_dir>                           \
    <suite1> [<suite2> ...]
```

| Argument | Class | Explanation |
|---|---|---|
| `<db_dir>` | **crucial** | Database containing raw BQRS result files from Phase 4. |
| `<suite>` | **crucial** | Must be the same suite references used in Phase 4.  CodeQL uses them to locate the BQRS files produced per-query. |
| `--format=sarif-latest` | **crucial** | Output format.  `sarif-latest` always targets the newest supported SARIF version (currently 2.1.0).  GitHub Code Scanning requires SARIF; other alert viewers (VS Code SARIF Viewer, Defender for DevOps) also consume it. |
| `--output=<path>` | **crucial** | Destination for the SARIF file.  The script writes to `_codeql/results/cpp.sarif`. |
| `-v` | convenience | Verbose output.  Required to capture the `CodeQL scanned N out of N C files …` coverage line, which `interpret-results` emits to stdout only in verbose mode. |
| `--sublanguage-file-coverage` | convenience | See Phase 1.  Both `database init` and `database interpret-results` must receive this flag for the coverage message to be emitted. |
| `--print-diagnostics-summary` | convenience | Prints a summary of any extraction warnings or errors.  Mirrors GitHub Actions; helps diagnose partial analysis. |
| `--print-metrics-summary` | convenience | Prints database metrics (lines of code, files analysed, etc.).  Mirrors GitHub Actions. |
| `--sarif-group-rules-by-pack` | convenience | Groups rules in the SARIF `rules` array by query pack rather than listing them flat.  Makes the SARIF file easier to navigate in viewers. |
| `--sarif-include-query-help=always` | convenience | Embeds query help text (markdown) inside the SARIF file.  Allows alert viewers to show remediation guidance offline. |

> **Note on `--sarif-add-baseline-file-info`:** The GitHub Actions
> `codeql-action` 2.25.5+ also passes this flag, which causes the coverage
> line to split C and C++ counts separately (_"3 out of 3 C files and 2 out
> of 2 C++ files"_).  The flag was introduced after CodeQL CLI 2.24.1 and is
> not available locally.  Without it, combined C/C++ files are reported as
> _"N out of N C files"_ (the extractor labels everything as C in the
> summary, even when C++ files are present).

---

### Phase 6 — Summary

```bash
codeql database print-baseline <db_dir>
```

Prints the baseline source file metrics (lines of code per language) that
CodeQL computed during `database init`.  Used purely for reporting — it has no
effect on the analysis.

The script also parses `cpp.sarif` directly to count total alerts by severity
level and list which rules fired.

---

## Bazel-specific issues

### The LD_PRELOAD tracing mechanism

CodeQL traces C/C++ by setting `LD_PRELOAD` to a shared library that intercepts
the `execve` syscall.  When a compiler process starts (e.g. `gcc`, `clang`),
that library runs first, records the command-line arguments, source paths, and
flags, and writes a TRAP file.

For this to work, `LD_PRELOAD` must survive from the shell running
`trace-command` all the way to the compiler binary.  Bazel can break this
chain in two ways:

#### Issue 1: Spawn strategy (sandbox type)

Bazel supports several sandboxing strategies that determine how action
environments are constructed:

| Strategy | Isolation mechanism | LD_PRELOAD survives? |
|---|---|---|
| `local` | None (runs in shell env) | ✓ |
| `processwrapper-sandbox` | Symlink forest, no namespaces | ✓ |
| `linux-sandbox` | Linux namespaces (`CLONE_NEWNS`, `CLONE_NEWUSER`) | ✗ (Bazel resets env) |
| `docker-sandbox` | Docker container | ✗ |

On Linux systems where `linux-sandbox` is available (most developer
workstations), Bazel uses it by default.  The script unconditionally injects
`--spawn_strategy=processwrapper-sandbox` as the **first** Bazel flag, giving
it higher precedence than any `.bazelrc` setting.

On GitHub Actions Ubuntu runners, user namespaces are disabled by the VM
configuration, so Bazel falls back to `processwrapper-sandbox` automatically.
That is why the GitHub workflow file needs no explicit spawn-strategy flag.

The script also inspects all `.bazelrc` files (system → user → workspace,
lowest to highest precedence) and warns if any of them set a spawn strategy
that would conflict with CodeQL tracing.

#### Issue 2: Action cache / pre-existing Bazel server

Even with the correct spawn strategy, tracing can silently fail if:

1. **Warm cache**: Bazel sees all outputs are up-to-date and skips the
   compiler.  No compiler invocation → no `execve` → no LD_PRELOAD hook →
   no TRAP files.  
   **Fix**: `bazel clean` before the traced build.

2. **Pre-existing server**: A Bazel server started *before*
   `trace-command` set `LD_PRELOAD` does not have that variable in its
   environment.  When it spawns compiler processes, they inherit the server's
   environment — not the traced one.  
   **Fix**: `bazel shutdown` before the traced build, so the subsequent
   `bazel build` starts a fresh server inside the traced environment.

Both fixes are automatically applied by the script.  Neither is required on
GitHub Actions, where the environment is always clean.

#### Issue 3: Bazel module system (Bzlmod) and rules_cc

Bazel 9+ moved `cc_binary`, `cc_library`, and `cc_test` out of the global
namespace.  Every `BUILD` file must now explicitly load them:

```python
# Required in Bazel 9+
load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library")
```

And `MODULE.bazel` must declare the dependency:

```python
bazel_dep(name = "rules_cc", version = "0.2.12")
```

Without this, the Bazel build fails before any compiler is invoked, and the
CodeQL database will be empty.

---

## Local vs. pipeline constraints and solutions

| Concern | GitHub Actions | Local (this script) |
|---|---|---|
| Fresh build environment | Always (new VM per run) | `bazel clean` before traced build |
| No pre-existing Bazel server | Always | `bazel shutdown` before traced build |
| Spawn strategy | Auto-fallback to `processwrapper-sandbox` (no user namespaces on the runner VM) | `--spawn_strategy=processwrapper-sandbox` injected explicitly |
| CodeQL CLI version | Pinned by `codeql-action` (currently 2.25.5) | Whatever is installed locally — older versions may lack some flags |
| Query pack download | `codeql-action` installs packs automatically | Packs are resolved from `~/.codeql/packages`; install once with `codeql pack download` |
| SARIF upload | `github/codeql-action/upload-sarif` uploads to GitHub Code Scanning | Only written locally to `_codeql/results/cpp.sarif` |
| Database path | Managed by the action, ephemeral | `_codeql/db/` at the project root (persistent, reusable) |
| Named configs | Not applicable (one fixed build configuration) | `-c <name>` maps to `--config=<name>` in `.bazelrc` |
| Multi-target builds | Workflow builds a single `//...` | Multiple positional `TARGET` arguments, one `trace-command` call per target |

### CLI flag syntax caveat

Bazel flag values that begin with `-` (e.g. `--config=debug`) cannot be
passed to `--bazel-flags` with a space separator because argparse interprets
the leading dash as a new option flag:

```bash
# Wrong: argparse error "expected one argument"
--bazel-flags '--config=debug'

# Correct: = binds the value before argparse sees it
--bazel-flags='--config=debug'

# Best: use the dedicated -c flag
-c debug
```

The `--` passthrough separator avoids the problem entirely for ad-hoc flags:

```bash
python3 tools/run_codeql.py //... -- --config=debug --jobs=4
```

---

## Script arguments reference

| Flag | Short | Default | Description |
|---|---|---|---|
| `TARGET` | — | `//...` | Bazel target(s) to build and analyse |
| `--source-root` | `-s` | project root | Source root for the CodeQL database.  Also sets `--build-cwd` when that flag is omitted. |
| `--build-cwd` | — | source root | Working directory for `bazel` commands.  Typically the Bazel workspace root. |
| `--config` | `-c` | — | Named Bazel config from `.bazelrc` (repeatable: `-c debug -c asan`) |
| `--suites` | — | `security-extended,security-and-quality` | Comma-separated query suites |
| `--language` | — | `cpp` | CodeQL language extractor |
| `--threads` | — | CPU count | Threads for Finalize and Run Queries phases |
| `--ram` | — | 80% of RAM | RAM limit in MB for Finalize and Run Queries phases |
| `--bazel-flags` | — | — | Extra flags forwarded to every `bazel build` (prefer `-c` or `--`) |
| `--clean` | — | false | Delete `_codeql/` before starting |

---

## Outlook: gaps and improvements

### What this script does differently from `codeql-action`

The `codeql-action` GitHub Action handles several concerns that this script
leaves to the user:

1. **CodeQL CLI installation**: The action downloads and pins a specific CLI
   version at runtime.  Locally, the CLI must be pre-installed.

2. **Query pack installation**: The action installs query packs into a
   temporary directory automatically.  Locally, `codeql pack download
   codeql/cpp-queries` must be run once, after which packs are cached in
   `~/.codeql/packages`.

3. **SARIF upload**: The action uploads the SARIF file to GitHub Code Scanning
   via the REST API.  Locally, only the file is written.

4. **`--sarif-add-baseline-file-info`**: Available in CLI ≥ 2.25.5 (used by
   the action); not yet available in 2.24.1.  Without it, the coverage summary
   cannot distinguish C files from C++ files.

5. **Autobuild**: For repos where the build command is unknown, `codeql-action`
   can attempt to infer and run the build automatically.  This script requires
   explicit Bazel targets.

### What is missing for use in any Bazel C/C++ repository

The following gaps would need to be addressed before the script can be
considered a general-purpose tool:

| Gap | Description | Possible solution |
|---|---|---|
| **Workspace detection** | The script expects `--source-root`/`--build-cwd` to point at a valid Bazel workspace.  It does not automatically discover nested workspaces or multi-package repositories. | Walk up from `cwd` looking for `MODULE.bazel`/`WORKSPACE` and offer detected root as default. |
| **Target discovery** | `//...` works for simple repos but may include non-C/C++ targets that fail or produce empty TRAP files when traced. | Query `bazel query 'kind("cc_.*", //...)'` and pass only C/C++ targets to `trace-command`. |
| **Autobuild fallback** | If the user does not know the right target, there is no fallback. | Implement autobuild logic similar to `codeql-action`: run `bazel build //...` and handle failures gracefully. |
| **Multi-language repos** | Repos with Rust + C/C++ require separate CodeQL databases (one per language).  The script only creates one. | Accept `--language` list; run the full pipeline once per language into separate database directories. |
| **Remote caching** | With a remote Bazel cache, `bazel clean` does not help — remote cache hits still skip compiler invocations. | Use `--noremote_accept_cached` or `--noremote_upload_local_results` during the traced build to force local compilation. |
| **Distributed builds** | Remote execution (RBE) runs compilers on worker machines where LD_PRELOAD cannot be injected. | Disable remote execution for the traced build with `--strategy=CppCompile=local` or `--local_test_jobs`. |
| **Windows support** | LD_PRELOAD is a Linux/macOS mechanism.  Windows tracing uses a different CodeQL mechanism. | Use `codeql database trace-command` with the `--working-dir` flag; the Windows extractor uses DLL injection instead. |
| **Incremental analysis** | Every run starts from scratch (`bazel clean` + `bazel shutdown`), which is slow for large repos. | Investigate `codeql database upgrade` and partial database population for true incremental local analysis. |
| **CLI version pinning** | The script uses whatever `codeql` is on `$PATH`, which may differ from CI. | Bundle a version check or a download step with a pinned version and hash. |
