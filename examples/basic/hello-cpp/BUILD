# C++ library
cc_library(
    name = "greeting",
    srcs = ["greeting.cpp"],
    hdrs = ["greeting.h"],
    visibility = ["//visibility:public"],
)

# C++ binary that uses the library
cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = [":greeting"],
)