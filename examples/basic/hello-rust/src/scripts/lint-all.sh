#!/bin/bash
# Complete repository linting script - use this to check all files for linting issues

echo "🔍 Linting all files in repository..."

# Markdown (when markdownlint is available after container rebuild)
echo "📝 Checking Markdown files..."
if command -v markdownlint &> /dev/null; then
    find . -name "*.md" -exec markdownlint {} \; || true
else
    echo "  ⚠️  markdownlint not available (install with: npm install -g markdownlint-cli)"
fi

# Python
echo "🐍 Checking Python files..."
find . -name "*.py" -exec black --check {} \; 2>/dev/null || true
find . -name "*.py" -exec pylint --errors-only {} \; 2>/dev/null || true

# Rust
echo "🦀 Checking Rust files..."
find . -name "*.rs" -exec rustfmt --check {} \; 2>/dev/null || true

# C/C++
echo "🔨 Checking C/C++ files..."
if command -v clang-format &> /dev/null; then
    find . \( -name "*.c" -o -name "*.cpp" -o -name "*.h" \) -exec clang-format --dry-run --Werror {} \; 2>/dev/null || true
else
    echo "  ⚠️  clang-format not available (install with: apt-get install clang-format)"
fi

# Bazel
echo "🏗️ Checking Bazel files..."
find . \( -name "BUILD*" -o -name "WORKSPACE*" -o -name "*.bzl" -o -name "MODULE.bazel" \) -exec buildifier -mode=check {} \; 2>/dev/null || true

# YAML
echo "📄 Checking YAML files..."
if command -v yamllint &> /dev/null; then
    find . \( -name "*.yaml" -o -name "*.yml" \) -exec yamllint {} \; 2>/dev/null || true
else
    echo "  ⚠️  yamllint not available (install with: pip3 install yamllint)"
fi

# Shell scripts
echo "🐚 Checking Shell scripts..."
if command -v shellcheck &> /dev/null; then
    find . -name "*.sh" -exec shellcheck {} \; 2>/dev/null || true
else
    echo "  ⚠️  shellcheck not available (install with: apt-get install shellcheck)"
fi

echo "✅ Linting complete!"
echo ""
echo "💡 To install missing linters, rebuild the devcontainer or run:"
echo "   - npm install -g markdownlint-cli"
echo "   - pip3 install yamllint"
echo "   - apt-get install clang-format shellcheck"