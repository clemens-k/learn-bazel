# Bazel Named Configurations Example

This example shows how Bazel **named configurations** (selected with
`--config=<name>`) let you switch between build modes without repeating long
flag strings on the command line.

## What is a Bazel config?

A config is a named group of Bazel flags defined in a `.bazelrc` file:

```
build:debug   --copt=-O0 --copt=-g --copt=-DDEBUG
build:release --copt=-O2 --copt=-DNDEBUG
build:asan    --copt=-fsanitize=address ...
```

Activate a config with `--config=<name>`:

```bash
bazel build //...                   # default flags only
bazel build --config=debug   //...  # debug build
bazel build --config=release //...  # release build
bazel build --config=asan    //...  # AddressSanitizer build
```

## Configs defined in this example

See [`.bazelrc`](.bazelrc) for the full definitions.

| Config      | Flags                         | Purpose                                             |
| ----------- | ----------------------------- | --------------------------------------------------- |
| *(default)* | `-Wall -Wextra -Wpedantic`    | All builds — warnings as documentation              |
| `debug`     | `-O0 -g -DDEBUG`              | Development: unoptimized, debug symbols, assertions |
| `release`   | `-O2 -DNDEBUG --strip=always` | Production: optimized, symbols stripped             |
| `asan`      | `-fsanitize=address -O1`      | Runtime memory-error detection                      |

## `.bazelrc` precedence

Bazel reads `.bazelrc` files in this order (later files override earlier ones;
command-line flags override everything):

```
/etc/bazel.bazelrc  (system)
~/.bazelrc           (user)
<workspace>/.bazelrc (this file)
command-line flags   (highest precedence)
```
