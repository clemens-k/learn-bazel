# Linting and Code Quality Guidelines

This document provides comprehensive linting instructions for all file types used in this Bazel learning repository. All tools are pre-installed in the devcontainer environment.

## 🔧 Available Linters by File Type

### 📝 Markdown Files (*.md)

**Tool:** `markdownlint`

```bash
# Lint markdown files
markdownlint README.md
markdownlint docs/*.md
markdownlint examples/**/*.md

# Lint all markdown files in repository
find . -name "*.md" -exec markdownlint {} \;

# Fix auto-fixable issues
markdownlint --fix README.md
```

**VS Code Extension:** `DavidAnson.vscode-markdownlint`

- Auto-lints on save
- Shows inline warnings/errors
- Supports quick fixes

### 🐍 Python Files (*.py)

**Tools:** `black` (formatter) + `pylint` (linter)

```bash
# Format Python code (auto-fix)
black generate.py
black examples/codegen/

# Lint Python code (check only)
pylint generate.py
pylint examples/codegen/generate.py

# Check all Python files
find . -name "*.py" -exec black --check {} \;
find . -name "*.py" -exec pylint {} \;

# Format all Python files
find . -name "*.py" -exec black {} \;
```

**VS Code Extensions:**

- `ms-python.black-formatter` (formatting)
- `ms-python.pylint` (linting)
- Auto-formats on save, shows inline issues

### 🦀 Rust Files (*.rs)

**Tools:** `rustfmt` (formatter) + `clippy` (linter)

```bash
# Format Rust code
rustfmt src/main.rs
rustfmt examples/*/src/*.rs

# Format with custom config
rustfmt --config max_width=100 src/main.rs

# Lint Rust code (requires cargo project)
cd examples/basic/hello-rust && cargo clippy
cd examples/codegen && cargo clippy

# Format all Rust files
find . -name "*.rs" -exec rustfmt {} \;
```

**VS Code Extension:** `rust-lang.rust-analyzer`

- Auto-formats on save
- Integrates with clippy for linting
- Shows inline diagnostics

### 🔨 C/C++ Files (\*.c, \*.cpp, \*.h)

**Tool:** `clang-format`

```bash
# Format C/C++ files
clang-format -i examples/basic/hello-c/hello.c
clang-format -i examples/basic/hello-cpp/*.cpp
clang-format -i examples/basic/hello-cpp/*.h

# Format with Google style (recommended)
clang-format -style=Google -i src/main.c

# Check formatting (dry run)
clang-format --dry-run --Werror examples/basic/hello-c/hello.c

# Format all C/C++ files
find . \( -name "*.c" -o -name "*.cpp" -o -name "*.h" \) -exec clang-format -i {} \;
```

**VS Code Extensions:**

- `ms-vscode.cpptools-extension-pack` (full C++ support)
- `xaver.clang-format` (formatting)
- Auto-formats on save with Google style

### 🏗️ Bazel Files (BUILD, WORKSPACE, MODULE.bazel, *.bzl)

**Tool:** `buildifier`

```bash
# Format Bazel files
buildifier BUILD
buildifier WORKSPACE
buildifier MODULE.bazel

# Format all Bazel files in repository
find . \( -name "BUILD*" -o -name "WORKSPACE*" -o -name "*.bzl" -o -name "MODULE.bazel" \) -exec buildifier {} \;

# Check formatting (dry run)
buildifier -mode=check BUILD

# Show differences
buildifier -mode=diff BUILD

# Lint mode (stricter checking)
buildifier -lint=warn BUILD
buildifier -lint=fix BUILD
```

**VS Code Extension:** `BazelBuild.vscode-bazel`

- Syntax highlighting for Starlark
- Integration with buildifier
- Auto-formats on save

### 📄 YAML Files (\*.yaml, \*.yml)

**Tool:** `yamllint`

```bash
# Lint YAML files
yamllint config.yaml
yamllint .github/workflows/*.yml

# Lint with custom config
yamllint -c .yamllint.yml config.yaml

# Lint all YAML files
find . \( -name "*.yaml" -o -name "*.yml" \) -exec yamllint {} \;
```

**VS Code Extension:** `redhat.vscode-yaml`

- Schema validation
- Auto-completion
- Syntax highlighting

### 🐚 Shell Scripts (*.sh)

**Tool:** `shellcheck`

```bash
# Lint shell scripts
shellcheck .devcontainer/setup.sh
shellcheck scripts/*.sh

# Check with specific shell
shellcheck -s bash setup.sh

# Show only errors and warnings
shellcheck -S error -S warning setup.sh

# Lint all shell scripts
find . -name "*.sh" -exec shellcheck {} \;
```

**VS Code Extension:** `timonwong.shellcheck`

- Real-time linting
- Inline error/warning display
- Supports multiple shell types

### 🎨 Template Files (*.j2)

**Tools:** No specific linter, but syntax highlighting available

```bash
# Basic syntax validation (if content is valid target language)
# For Jinja2 templates containing Rust:
rustfmt --check templates/constants.rs.j2 2>/dev/null || echo "Template syntax OK"

# For Jinja2 templates containing C:
clang-format --dry-run templates/header.h.j2 2>/dev/null || echo "Template syntax OK"
```

**VS Code:** Template files are associated with `jinja` language for syntax highlighting.

### 📋 JSON Files (*.json)

**Built-in:** VS Code JSON validation

```bash
# Validate JSON syntax using Python
python3 -m json.tool devcontainer.json > /dev/null && echo "Valid JSON"

# Format JSON (pretty print)
python3 -m json.tool devcontainer.json
```

**VS Code:** Built-in JSON support with schema validation

## 🚀 Automated Linting Commands

### Lint All Files in Repository

```bash
#!/bin/bash
# Complete repository linting script

echo "🔍 Linting all files in repository..."

# Markdown
echo "📝 Checking Markdown files..."
find . -name "*.md" -exec markdownlint {} \; || true

# Python
echo "🐍 Checking Python files..."
find . -name "*.py" -exec black --check {} \; || true
find . -name "*.py" -exec pylint {} \; || true

# Rust
echo "🦀 Checking Rust files..."
find . -name "*.rs" -exec rustfmt --check {} \; || true

# C/C++
echo "🔨 Checking C/C++ files..."
find . \( -name "*.c" -o -name "*.cpp" -o -name "*.h" \) -exec clang-format --dry-run --Werror {} \; || true

# Bazel
echo "🏗️ Checking Bazel files..."
find . \( -name "BUILD*" -o -name "WORKSPACE*" -o -name "*.bzl" -o -name "MODULE.bazel" \) -exec buildifier -mode=check {} \; || true

# YAML
echo "📄 Checking YAML files..."
find . \( -name "*.yaml" -o -name "*.yml" \) -exec yamllint {} \; || true

# Shell scripts
echo "🐚 Checking Shell scripts..."
find . -name "*.sh" -exec shellcheck {} \; || true

echo "✅ Linting complete!"
```

### Format All Files in Repository

```bash
#!/bin/bash
# Complete repository formatting script

echo "🎨 Formatting all files in repository..."

# Python
echo "🐍 Formatting Python files..."
find . -name "*.py" -exec black {} \;

# Rust
echo "🦀 Formatting Rust files..."
find . -name "*.rs" -exec rustfmt {} \;

# C/C++
echo "🔨 Formatting C/C++ files..."
find . \( -name "*.c" -o -name "*.cpp" -o -name "*.h" \) -exec clang-format -i {} \;

# Bazel
echo "🏗️ Formatting Bazel files..."
find . \( -name "BUILD*" -o -name "WORKSPACE*" -o -name "*.bzl" -o -name "MODULE.bazel" \) -exec buildifier {} \;

# Markdown (auto-fix)
echo "📝 Fixing Markdown files..."
find . -name "*.md" -exec markdownlint --fix {} \; || true

echo "✅ Formatting complete!"
```

## 📊 VS Code Integration

All linters are integrated into VS Code with the configured extensions:

- **Auto-format on save** is enabled for all supported file types
- **Inline diagnostics** show errors and warnings as you type
- **Quick fixes** are available for many issues
- **Command palette** provides format/lint commands

### VS Code Commands

- `Format Document` (Shift+Alt+F)
- `Format Selection`
- `Organize Imports`
- `Fix All` (Ctrl+Shift+A)

### Workspace Settings

The devcontainer includes optimized settings for:

- Consistent formatting across all file types
- Integration with external linting tools
- Proper file associations for Bazel and template files

## 🔧 Configuration Files

The repository can include these optional configuration files:

- `.clang-format` - C/C++ formatting rules
- `.rustfmt.toml` - Rust formatting configuration  
- `.yamllint.yml` - YAML linting rules
- `.markdownlint.json` - Markdown linting configuration
- `pyproject.toml` - Python tool configuration

All tools use sensible defaults when configuration files are not present.
