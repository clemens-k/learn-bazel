load("@rules_rust//rust:defs.bzl", "rust_binary", "rust_library")

# Rust library
rust_library(
    name = "greeting",
    srcs = ["src/lib.rs"],
    edition = "2021",
    visibility = ["//visibility:public"],
)

# Rust binary that uses the library
rust_binary(
    name = "main",
    srcs = ["src/main.rs"],
    edition = "2021",
    deps = [":greeting"],
)