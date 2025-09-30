load("@rules_rust//rust:defs.bzl", "rust_binary")

# Python code generator
py_binary(
    name = "generator",
    srcs = ["generate.py"],
    data = [
        "config.yaml",
        "//templates:all_templates",
    ],
    deps = [],  # Add Jinja2 dependency in real project
)

# Generate C header
genrule(
    name = "generate_c_header",
    srcs = [
        "config.yaml",
        "//templates:header.h.j2",
    ],
    outs = ["generated/config.h"],
    cmd = "$(location :generator) c $(location config.yaml) $(location //templates:header.h.j2) $@",
    tools = [":generator"],
)

# Generate Rust constants
genrule(
    name = "generate_rust_constants",
    srcs = [
        "config.yaml",
        "//templates:constants.rs.j2",
    ],
    outs = ["generated/constants.rs"],
    cmd = "$(location :generator) rust $(location config.yaml) $(location //templates:constants.rs.j2) $@",
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
        ":generate_rust_constants",
    ],
    edition = "2021",
)