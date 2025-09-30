# Devcontainer Configuration

This directory contains the configuration for a **reproducible development environment** using VS Code devcontainers.

## 🐳 What's Included

### Base Environment

- **Ubuntu 22.04** base image
- **Zsh** with Oh My Zsh configuration
- **Git** with helpful aliases

### Build Tools

- **Bazel 7.0.0** - Latest stable version
- **GCC & Clang** - C/C++ compilers
- **Rust 1.75.0** - Rust toolchain
- **Python 3.11** - For code generation scripts
- **Buildifier** - Bazel code formatter

### VS Code Extensions

- **Bazel** - Official Bazel support
- **C/C++** - Microsoft C++ extension pack
- **Rust Analyzer** - Advanced Rust support
- **Python** - Python development tools
- **YAML** - Configuration file support
- **GitHub Copilot** - AI assistance
- **GitLens** - Enhanced Git integration

## 🚀 Quick Start

### Prerequisites

- **VS Code** with Dev Containers extension
- **Docker** running on your machine

### Setup

1. **Clone** this repository
2. **Open** in VS Code  
3. **Click** "Reopen in Container" when prompted (or use Command Palette: "Dev Containers: Reopen in Container")
4. **Wait** for the container to build and setup (first time takes ~5-10 minutes)
5. **Start coding!**

### Testing the Setup

After the container is ready, test it:

```bash
# Check Bazel installation
bazel version

# Build a simple example
cd examples/basic/hello-c
bazel build :main
bazel run :main
```

## ⚙️ Configuration Details

### Bazel Configuration

The container sets up optimal Bazel configuration in `~/.bazelrc`:

```bash
# Performance optimizations
build --local_ram_resources=HOST_RAM*0.75
build --local_cpu_resources=HOST_CPUS
build --disk_cache=~/.cache/bazel

# C++ standards
build --cxxopt=-std=c++17

# Better output
build --color=yes
build --verbose_failures
```

### Persistent Cache

Bazel's build cache is mounted to `.bazel-cache/` in your project root, ensuring:

- **Fast rebuilds** across container restarts
- **Shared cache** between different projects
- **Persistent artifacts** even after container updates

### Useful Aliases

The setup includes helpful shell aliases:

```bash
# Bazel commands
bb    # bazel build
br    # bazel run
bt    # bazel test
bq    # bazel query
bc    # bazel clean

# File operations
ll    # ls -la
tree  # tree (excluding bazel-* dirs)
```

## 🔧 Customization

### Adding Tools

Edit `.devcontainer/setup.sh` to install additional tools:

```bash
# Add to setup.sh
sudo apt-get install -y your-package
pip3 install --user your-python-package
```

### VS Code Settings

Modify `.devcontainer/devcontainer.json` to adjust VS Code configuration:

```json
"settings": {
    "your.setting": "value"
}
```

### Extensions

Add VS Code extensions in `devcontainer.json`:

```json
"extensions": [
    "publisher.extension-name"
]
```

## 🐛 Troubleshooting

### Container Won't Start

- Ensure Docker is running
- Check Docker has enough resources (4GB+ RAM recommended)
- Try "Remote-Containers: Rebuild Container"

### Bazel Build Failures

- Check disk space: `df -h`
- Clear Bazel cache: `bazel clean --expunge`
- Verify tools: `bazel info`

### Performance Issues

- Increase Docker resource limits
- Use bind mounts for better I/O performance
- Enable BuildKit for faster Docker builds

## 📚 Further Reading

- [VS Code Devcontainers Documentation](https://code.visualstudio.com/docs/remote/containers)
- [Bazel Installation Guide](https://docs.bazel.build/install.html)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)

---

*This devcontainer provides a consistent, reproducible environment for
learning and developing with Bazel across different machines and team members.*
