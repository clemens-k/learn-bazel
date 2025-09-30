#!/bin/bash
set -e

echo "🚀 Setting up Bazel learning environment..."

# Update package lists
sudo apt-get update

# Install essential build tools
echo "📦 Installing build tools..."
sudo apt-get install -y \
    build-essential \
    clang \
    clang-format \
    llvm \
    curl \
    wget \
    unzip \
    git \
    pkg-config \
    graphviz \
    tree \
    shellcheck

# Install Bazel
echo "🔧 Installing Bazel..."
BAZEL_VERSION="8.4.1"
wget -O bazel-installer.sh "https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/bazel-${BAZEL_VERSION}-installer-linux-x86_64.sh"
chmod +x bazel-installer.sh
sudo ./bazel-installer.sh
rm bazel-installer.sh

# Install Buildifier (Bazel formatter)
echo "🎨 Installing Buildifier..."
BUILDIFIER_VERSION="8.2.1"
wget -O buildifier "https://github.com/bazelbuild/buildtools/releases/download/v${BUILDIFIER_VERSION}/buildifier-linux-amd64"
chmod +x buildifier
sudo mv buildifier /usr/local/bin/

# Install Python dependencies for code generation
echo "🐍 Installing Python dependencies..."
pip3 install --user \
    jinja2 \
    pyyaml \
    black \
    pylint \
    yamllint

# Install Node.js for additional linting tools
echo "📦 Installing Node.js and npm packages..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Markdown linter
sudo npm install -g markdownlint-cli

# Set up Bazel configuration
echo "⚙️ Configuring Bazel..."
mkdir -p ~/.bazelrc.d
cat > ~/.bazelrc << 'EOF'
# Common Bazel configuration
build --symlink_prefix=bazel-
build --color=yes
build --show_progress_rate_limit=5
build --show_timestamps
build --verbose_failures

# C++ configuration
build --cxxopt=-std=c++17
build --host_cxxopt=-std=c++17

# Rust configuration, doesn't work as not all project use @rust_rules
# build --@rules_rust//:rustfmt.toml=//.rustfmt.toml

# Performance optimizations, what's the default?
# build --local_resources=memory=HOST_RAM*.75,cpu=HOST_CPUS

# Cache configuration
build --disk_cache=~/.cache/bazel
EOF

# Create Rust format configuration
echo "🦀 Setting up Rust configuration..."
cat > ~/.rustfmt.toml << 'EOF'
max_width = 100
tab_spaces = 4
newline_style = "Unix"
use_small_heuristics = "Default"
reorder_imports = true
reorder_modules = true
remove_nested_parens = true
EOF

# Set up Git configuration helpers
echo "📋 Setting up Git helpers..."
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm commit
git config --global alias.lg "log --oneline --graph --all --decorate"

# Create useful aliases
echo "🔗 Setting up shell aliases..."
cat >> ~/.zshrc << 'EOF'

# Bazel aliases
alias bb='bazel build'
alias br='bazel run'
alias bt='bazel test'
alias bq='bazel query'
alias bc='bazel clean'
alias bi='bazel info'

# Quick navigation
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'

# Development helpers
alias tree='tree -I "bazel-*"'
EOF

# Ensure cache directory exists
mkdir -p ~/.cache/bazel

echo "✅ Bazel learning environment setup complete!"
echo "🎯 You can now start with: cd examples/basic/hello-c && bazel run :main"
echo "📚 Check the README.md for learning paths and examples"

# Display versions
echo ""
echo "📊 Installed versions:"
echo "Bazel: $(bazel version | head -1)"
echo "GCC: $(gcc --version | head -1)"
echo "Clang: $(clang --version | head -1)"
echo "Rust: $(rustc --version)"
echo "Python: $(python3 --version)"
echo "Buildifier: $(buildifier --version)"