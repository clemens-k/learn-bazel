load("@rules_cc//cc:defs.bzl", "cc_binary")
load("@rules_python//python:defs.bzl", "py_binary")
load("@rules_rust//rust:defs.bzl", "rust_binary", "rust_library")

# Python code generator
py_binary(
    name = "generator",
    srcs = ["generate.py"],
    data = [
        "config.yaml",
    ],
    main = "generate.py",
    deps = [],
)

# Generate C header
genrule(
    name = "generate_c_header",
    srcs = [
        "config.yaml",
        "//templates:all_templates",
    ],
    outs = ["generated/config.h"],
    cmd = "$(location :generator) c $(location config.yaml) templates/header.h.j2 $@",
    tools = [":generator"],
)

# Generate Rust constants
genrule(
    name = "generate_rust_constants",
    srcs = [
        "config.yaml",
        "//templates:all_templates",
    ],
    outs = ["generated/constants.rs"],
    cmd = "$(location :generator) rust $(location config.yaml) templates/constants.rs.j2 $@",
    tools = [":generator"],
)

# C application using generated header
cc_binary(
    name = "c_app",
    srcs = [
        "src/main.c",
        ":generate_c_header",
    ],
    includes = ["generated"],
)

# Rust application using generated constants
rust_binary(
    name = "rust_app",
    srcs = [
        "src/main.rs",
    ],
    edition = "2021",
    deps = [":rust_constants_lib"],
)

# Create a Rust library with the generated constants
rust_library(
    name = "rust_constants_lib",
    srcs = [":generate_rust_constants"],
    crate_name = "rust_constants_lib",
    edition = "2021",
)
