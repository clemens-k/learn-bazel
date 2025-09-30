# Code Generation with Bazel

This example demonstrates how to use **Python and Jinja2** for build-time code generation in Bazel, creating C headers and Rust code from templates.

## 📁 Project Structure

```
codegen/
├── WORKSPACE                  # Workspace with Python rules
├── BUILD                      # Build configuration
├── generate.py                # Python code generator script
├── config.yaml                # Configuration data
├── templates/
│   ├── header.h.j2            # C header template
│   └── constants.rs.j2        # Rust constants template
└── src/
    ├── main.c                 # C program using generated header
    └── main.rs                # Rust program using generated constants
```

## 🚀 How It Works

1. **Configuration**: `config.yaml` contains data for code generation
2. **Templates**: Jinja2 templates define the structure of generated code
3. **Generator**: Python script processes templates with configuration data
4. **Integration**: Bazel rules orchestrate the generation and compilation

## 🔧 Build and Run

```bash
# Generate and build C version
bazel build :c_app
bazel run :c_app

# Generate and build Rust version
bazel build :rust_app
bazel run :rust_app

# Build everything
bazel build //...
```

## 🔍 Key Concepts

- **genrule**: Bazel rule for custom code generation
- **py_binary**: Python executable for the generator
- **Template Engine**: Jinja2 for flexible code generation
- **Data-Driven**: Configuration drives code generation
- **Multi-Language**: Same data generates code for different languages

## 📋 Use Cases

This pattern is useful for:
- **Configuration Management**: Generate code from config files
- **API Definitions**: Generate client/server code from specs
- **Constants**: Generate language-specific constants
- **Boilerplate**: Reduce repetitive code
- **Protocol Buffers Alternative**: Custom serialization formats