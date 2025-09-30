# Core Concepts

## 🎯 Fundamental Building Blocks

Understanding Bazel requires grasping several interconnected concepts that work together to create a powerful and scalable build system.

### The Big Picture

```
Workspace → Packages → Targets → Rules → Actions → Artifacts
    ↓         ↓         ↓        ↓        ↓         ↓
  Project   Modules   Build    How to   What to   Output
   Root     /Dirs    Units     Build    Execute   Files
```

## 🏗️ Workspace

### Definition
A **workspace** is the root directory of your project containing all source code and a `WORKSPACE` (or `WORKSPACE.bazel`) file.

### Key Characteristics
- **Single Root**: One workspace per project
- **Self-Contained**: All dependencies are explicitly declared
- **Hermetic**: Isolated from the host system

### WORKSPACE File
```python
# WORKSPACE or WORKSPACE.bazel
workspace(name = "my_project")

# External dependencies
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_java",
    urls = ["https://github.com/bazelbuild/rules_java/archive/refs/tags/5.0.0.tar.gz"],
    sha256 = "...",
    strip_prefix = "rules_java-5.0.0",
)
```

### Modern Alternative: MODULE.bazel
```python
# MODULE.bazel (newer approach)
module(
    name = "my_project",
    version = "1.0.0",
)

bazel_dep(name = "rules_cc", version = "0.0.2")
bazel_dep(name = "rules_rust", version = "0.30.0")
bazel_dep(name = "rules_python", version = "0.25.0")
```

## 📦 Packages

### Definition
A **package** is a directory containing a `BUILD` (or `BUILD.bazel`) file, representing a collection of related files and targets.

### Package Structure
```
my_project/
├── WORKSPACE
├── src/
│   ├── BUILD          # Package: //src
│   ├── main/
│   │   ├── BUILD      # Package: //src/main
│   │   └── java/
│   └── test/
│       ├── BUILD      # Package: //src/test
│       └── java/
└── tools/
    └── BUILD          # Package: //tools
```

### Package Names
- **Root Package**: `//` (contains WORKSPACE)
- **Subpackages**: `//src`, `//src/main`, `//src/test`
- **Relative References**: `:target_name` within same package

## 🎯 Targets

### Definition
A **target** is anything that Bazel can build - files, rules, or package groups.

### Types of Targets

**1. Rule Targets**
```python
# BUILD file
java_binary(
    name = "my_app",           # Target name
    srcs = ["Main.java"],      # Source files
    main_class = "com.example.Main",
    deps = [":my_library"],    # Dependencies
)

java_library(
    name = "my_library",
    srcs = ["Library.java"],
    visibility = ["//visibility:public"],
)
```

**2. File Targets**
```python
# Source files are implicit targets
# //src:Main.java
# //src:Library.java

# Generated files are also targets
genrule(
    name = "generate_config",
    srcs = ["config.template"],
    outs = ["config.properties"],
    cmd = "sed 's/VERSION/1.0/' $< > $@",
)
```

**3. Package Group Targets**
```python
package_group(
    name = "internal_packages",
    packages = [
        "//src/main/...",
        "//src/test/...",
    ],
)
```

### Target Labels
```python
# Full label format: @workspace//package:target
"@my_project//src/main:my_app"

# Within same workspace: //package:target
"//src/main:my_app"

# Within same package: :target
":my_app"

# External workspace
"@external_repo//package:target"
```

## 📋 Rules

### Definition
**Rules** define how to build targets - they specify inputs, outputs, and the commands to transform inputs into outputs.

### Built-in Rules

**Language-Specific Rules**:
```python
# C++
cc_binary(name = "app", srcs = ["main.cc"])
cc_library(name = "lib", srcs = ["lib.cc"], hdrs = ["lib.h"])
cc_test(name = "test", srcs = ["test.cc"])

# Rust
rust_binary(name = "app", srcs = ["main.rs"])
rust_library(name = "lib", srcs = ["lib.rs"])
rust_test(name = "test", srcs = ["test.rs"])

# Python
py_binary(name = "app", srcs = ["main.py"])
py_library(name = "lib", srcs = ["lib.py"])
py_test(name = "test", srcs = ["test.py"])
```

**Generic Rules**:
```python
# Generate files
genrule(
    name = "generate_version",
    outs = ["version.h"],
    cmd = "echo '#define VERSION \"1.0\"' > $@",
)

# Copy files
filegroup(
    name = "configs",
    srcs = glob(["*.conf"]),
)

# Create archives
pkg_tar(
    name = "release",
    srcs = [":app"],
    package_dir = "/usr/local/bin",
)
```

### Custom Rules (Starlark)
```python
# rules.bzl
def _custom_rule_impl(ctx):
    output = ctx.actions.declare_file(ctx.label.name + ".out")
    ctx.actions.run_shell(
        inputs = ctx.files.srcs,
        outputs = [output],
        command = "cat {} > {}".format(
            " ".join([f.path for f in ctx.files.srcs]),
            output.path
        ),
    )
    return [DefaultInfo(files = depset([output]))]

custom_rule = rule(
    implementation = _custom_rule_impl,
    attrs = {
        "srcs": attr.label_list(allow_files = True),
    },
)
```

## ⚙️ Actions

### Definition
**Actions** are the commands that Bazel executes to build targets. They are generated by rules during the analysis phase.

### Action Properties
- **Inputs**: Files the action reads
- **Outputs**: Files the action creates
- **Command**: Shell command or executable to run
- **Environment**: Environment variables
- **Working Directory**: Where the command runs

### Action Example
```python
# C++ compilation example:
g++ -std=c++17 -O2 -c main.cc -o main.o

# Inputs: main.cc, header files
# Outputs: main.o
# Command: g++ with specific arguments

# Rust compilation example:
rustc --crate-type bin main.rs -o main

# Inputs: main.rs, dependency crates
# Outputs: main (binary)
# Command: rustc with crate configuration
```

### Action Graph
```
Source Files → Actions → Artifacts → More Actions → Final Artifacts
    ↓             ↓          ↓            ↓              ↓
  main.cc    → [g++]   → main.o    → [linker] → my_app
  lib.cc     → [g++]   → lib.o     ↗
  
  main.rs    → [rustc] → my_rust_app (all-in-one compilation)
  lib.rs     → [rustc] → libmy_lib.rlib → [rustc] → final_app
```

## 🗂️ Build Graph

### Definition
The **build graph** is a directed acyclic graph (DAG) representing all dependencies between targets.

### Graph Structure
```
          my_app (cc_binary)
              ↓
         my_library (cc_library)
              ↓
    ┌─────────────────┐
    ↓                 ↓
common_utils      network_client
(cc_library)      (rust_library)
    ↓                 ↓
third_party_lib   external_crate
                  (external dependency)
```

### Analysis Phase
1. **Parse** BUILD files
2. **Resolve** dependencies
3. **Build** target graph
4. **Generate** actions
5. **Optimize** execution plan

### Execution Phase
1. **Topological Sort** of actions
2. **Parallel Execution** where possible
3. **Caching** of results
4. **Sandboxing** for isolation

## 🔧 Attributes

### Common Attributes
```python
cc_library(
    name = "my_library",              # Required: target name
    srcs = ["lib.cc"],               # Source files
    hdrs = ["lib.h"],                # Header files
    deps = [":common_utils"],        # Dependencies
    visibility = ["//visibility:public"],  # Who can depend on this
    data = ["config.txt"],           # Runtime data files
    copts = ["-std=c++17"],          # Compiler options
    tags = ["manual", "integration"], # Metadata tags
)

rust_library(
    name = "my_rust_lib",
    srcs = ["lib.rs"],
    deps = [":common_rust"],
    visibility = ["//visibility:public"],
    crate_features = ["serde"],      # Rust-specific: crate features
    edition = "2021",                # Rust edition
)
```

### Attribute Types
- **label**: Reference to another target
- **label_list**: List of target references
- **string**: Text value
- **string_list**: List of text values
- **bool**: True/false value
- **int**: Numeric value

## 🎨 Starlark Configuration Language

### Why Starlark?
- **Familiar**: Python-like syntax
- **Safe**: No arbitrary code execution
- **Deterministic**: Same inputs = same outputs
- **Analyzable**: Can be parsed and understood

### Basic Syntax
```python
# Variables
name = "my_app"
sources = ["main.cc", "utils.cc"]
rust_sources = ["main.rs", "utils.rs"]

# Functions
def get_sources(lang):
    if lang == "cpp":
        return glob(["*.cc", "*.cpp"])
    elif lang == "rust":
        return glob(["*.rs"])
    elif lang == "python":
        return glob(["*.py"])
    else:
        fail("Unsupported language: " + lang)

# Lists and dictionaries
deps = [":common", ":utils"]
config = {
    "debug": True,
    "version": "1.0",
}

# Conditionals with different languages
cc_library(
    name = "lib",
    srcs = glob(["*.cc"]),
    deps = select({
        "//conditions:debug": [":debug_utils"],
        "//conditions:default": [],
    }),
    copts = select({
        "//conditions:debug": ["-g", "-O0"],
        "//conditions:default": ["-O2"],
    }),
)

rust_binary(
    name = "rust_app",
    srcs = ["main.rs"],
    deps = select({
        "//conditions:feature_x": [":feature_x_lib"],
        "//conditions:default": [],
    }),
)
```

## 🔄 Build Lifecycle

### Complete Build Process
```
1. Loading Phase
   ├── Parse WORKSPACE/MODULE.bazel
   ├── Resolve external dependencies
   ├── Parse BUILD files
   └── Create package objects

2. Analysis Phase
   ├── Build target graph
   ├── Apply rules
   ├── Generate actions
   ├── Validate dependencies
   └── Create execution plan

3. Execution Phase
   ├── Execute actions (parallel)
   ├── Check cache for results
   ├── Run in sandbox
   ├── Store outputs
   └── Report results
```

### Incremental Builds
Bazel only rebuilds what changed:
- **File Changes**: Detected automatically
- **Dependency Changes**: Propagated through graph
- **Rule Changes**: Invalidate affected targets
- **Configuration Changes**: May require full rebuild

## 🏷️ Labels and Visibility

### Label Resolution
```python
# From //src/main:BUILD
deps = [
    ":utils",                    # //src/main:utils
    "//src/common:types",        # Absolute reference
    "@external_repo//pkg:lib",   # External dependency
]
```

### Visibility Control
```python
# Private (default)
cc_library(
    name = "internal_lib",
    visibility = ["//visibility:private"],  # Only this package
)

# Public
rust_library(
    name = "public_lib",
    visibility = ["//visibility:public"],   # Anyone can use
)

# Specific packages
cc_library(
    name = "team_lib",
    visibility = [
        "//src/main/...",          # All subpackages
        "//tools:__pkg__",         # Specific package only
    ],
)
```

---

*These core concepts form the foundation of Bazel's power - understanding 
them enables you to build complex, scalable, and maintainable build configurations.*