# Hello C Example

The simplest possible Bazel C project - a basic application that prints "Hello, Bazel from C!"

## 📁 Project Structure

```
hello-c/
├── WORKSPACE              # Defines the workspace root
├── BUILD                  # Build configuration
└── hello.c                # C source code
```

## 🚀 How to Build and Run

```bash
# Build the target
bazel build :main

# Run the application
bazel run :main

# Run with arguments
bazel run :main -- arg1 arg2 arg3
```

## 🔍 Key Concepts

- **cc_binary**: Rule for building C/C++ executables
- **srcs**: Source files to compile
- **Implicit dependencies**: Bazel automatically finds system libraries (libc)

## 🧪 Try This

```bash
# See the actual compilation command
bazel build :main --subcommands

# Build with debug information
bazel build :main --copt=-g

# Build with optimizations
bazel build :main --copt=-O2
```