# Hello C++ Example

A C++ project demonstrating libraries and binaries with Bazel.

## 📁 Project Structure

```
hello-cpp/
├── WORKSPACE              # Defines the workspace root
├── BUILD                  # Build configuration
├── greeting.h             # Header file
├── greeting.cpp           # Library implementation
└── main.cpp               # Main application
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
bazel run :main -- C++ Bazel rocks
```

## 🔍 Key Concepts

- **cc_library**: Rule for building C++ libraries
- **cc_binary**: Rule for building C++ executables
- **hdrs**: Header files that are part of the public interface
- **srcs**: Source files to compile
- **deps**: Dependencies on other targets
- **visibility**: Controls which packages can depend on this target

## 🧪 Advanced Usage

```bash
# See the dependency graph
bazel query --output=graph //... | dot -Tpng > deps.png

# Build with different C++ standard
bazel build :main --cxxopt='-std=c++17'

# Build with debug symbols
bazel build :main --copt=-g --cxxopt=-g

# Show compilation commands
bazel build :main --subcommands
```

## 📋 What This Example Shows

1. **Separation of Concerns**: Library vs application code
2. **Header Management**: Public interface via `.h` files
3. **Dependency Management**: Binary depends on library
4. **Modern C++**: Using STL containers and methods
5. **Build Modularity**: Can build library independently