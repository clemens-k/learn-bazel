# Hello Rust Example

A Rust project demonstrating libraries and binaries with Bazel.

## 📁 Project Structure

```
hello-rust/
├── WORKSPACE              # Defines workspace and Rust rules
├── BUILD                  # Build configuration
└── src/
    ├── lib.rs             # Library implementation
    └── main.rs            # Main application
```

## 🚀 How to Build and Run

```bash
# Build everything
bazel build //...

# Build just the library
bazel build :greeting

# Build and run the main application
bazel run :main

# Run with arguments
bazel run :main -- Rust Bazel awesome
```

## 🔍 Key Concepts

- **rules_rust**: External ruleset for Rust support
- **rust_library**: Rule for building Rust libraries (crates)
- **rust_binary**: Rule for building Rust executables
- **edition**: Rust edition (2021 is current)
- **deps**: Dependencies on other Rust targets

## 🧪 Advanced Usage

```bash
# Run tests
bazel test :greeting

# Build in release mode
bazel build :main --compilation_mode=opt

# See Rust compilation commands
bazel build :main --subcommands

# Check the dependency graph
bazel query --output=graph //... | dot -Tpng > deps.png
```

## 📋 What This Example Shows

1. **Rust Integration**: How to set up Rust rules in Bazel
2. **Library Structure**: Creating reusable Rust libraries
3. **Modern Rust**: Using Rust 2021 edition features
4. **Documentation**: Rust doc comments and testing
5. **Error Handling**: Rust's ownership and borrowing in practice

## 🔧 Rust-Specific Features

- **Cargo Compatibility**: Can integrate with existing Cargo projects
- **Cross-Compilation**: Bazel supports Rust cross-compilation
- **Incremental Compilation**: Fast rebuilds with Rust's incremental compilation
- **Testing**: Built-in support for Rust unit tests