# Basic Bazel Examples

This directory contains simple examples to get you started with Bazel using **C, C++, and Rust**. Each example demonstrates a specific concept and can be built independently.

## 📁 Directory Structure

```
basic/
├── README.md                 # This file
├── hello-c/                  # Minimal C application
├── hello-cpp/                # Simple C++ application with classes
├── hello-rust/               # Basic Rust binary
├── multi-target/             # Multiple targets in one package
├── dependencies/             # Inter-target dependencies
└── external-deps/            # External library dependencies
```

## 🚀 Quick Start

1. **Install Bazel**: Follow instructions at [bazel.build](https://bazel.build)
2. **Navigate to example**: `cd examples/basic/hello-world`
3. **Build**: `bazel build //...`
4. **Run**: `bazel run :main`

## 📚 Learning Progression

### 1. Hello C
Start here to understand the basics:
- WORKSPACE setup
- Simple BUILD file
- Basic cc_binary rule

### 2. Hello C++
Learn C++ specifics:
- Headers and source files
- cc_library and cc_binary
- C++ compilation flags

### 3. Hello Rust
Rust integration:
- Rust rules setup
- rust_binary and rust_library
- Cargo integration patterns

### 4. Multi-Target
Learn about multiple targets:
- Multiple rules in one BUILD file
- Local dependencies
- File organization

### 5. Dependencies
Understand dependency management:
- Inter-package dependencies
- Target visibility
- Dependency graphs

### 6. External Dependencies
Work with external libraries:
- System libraries
- Third-party packages
- Dependency resolution

## 🛠️ Common Commands

```bash
# Build everything
bazel build //...

# Build specific target
bazel build //hello-c:main
bazel build //hello-cpp:main
bazel build //hello-rust:main

# Run a binary
bazel run //hello-c:main
bazel run //hello-cpp:main
bazel run //hello-rust:main

# Test everything
bazel test //...

# Clean build outputs
bazel clean

# Show build graph
bazel query --output=graph //... | dot -Tpng > graph.png

# Show C++ compilation commands
bazel build //hello-cpp:main --subcommands
```

## 💡 Tips for Beginners

1. **Start Small**: Begin with the hello-world example
2. **Read BUILD Files**: They're the key to understanding Bazel
3. **Use bazel query**: Explore dependencies and targets
4. **Check bazel info**: Understand your Bazel setup
5. **Read Error Messages**: They're usually helpful and specific

## 🔗 Next Steps

After completing these examples:
1. Explore [Rust-Specific Examples](../rust/)
2. Learn about [Code Generation](../codegen/)
3. Try [Advanced Patterns](../advanced/)
4. Read the [Official Documentation](https://docs.bazel.build/)

---

*These examples provide hands-on experience with Bazel's core concepts using modern systems programming languages.*