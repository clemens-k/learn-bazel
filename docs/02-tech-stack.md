# Tech Stack & Architecture

## 🔧 Core Implementation

### Primary Programming Languages

**Java** (Primary Implementation)

- **Percentage**: ~80% of codebase
- **Components**: Core build engine, rule execution, dependency analysis
- **Why Java**:
  - Cross-platform compatibility
  - Strong ecosystem and tooling
  - Excellent performance for long-running processes
  - Robust garbage collection for large data structures
  - Thread-safe collections for concurrent operations

**C++** (Performance-Critical Components)

- **Percentage**: ~15% of codebase
- **Components**: File system operations, process management, native optimizations
- **Why C++**:
  - Direct system calls for better performance
  - Memory management control
  - Integration with existing native tools
  - Platform-specific optimizations

**Starlark** (Configuration Language)

- **Percentage**: ~3% of codebase
- **Purpose**: BUILD file syntax, rules definition, configuration
- **Why Starlark**:
  - Python-like syntax (familiar to developers)
  - Deterministic execution (no side effects)
  - Sandboxed execution for security
  - Designed specifically for configuration

**Other Languages**

- **Shell Scripts**: ~2% - Build scripts, installation, testing
- **Python**: Build tools, code generation, testing infrastructure
- **Protocol Buffers**: Data serialization and RPC definitions

## 🏗️ Architecture Overview

### High-Level Architecture

```txt
┌─────────────────────────────────────────────────────────────┐
│                    Bazel Client (CLI)                       │
├─────────────────────────────────────────────────────────────┤
│                    Bazel Server                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Analysis      │  │   Execution     │  │   Action     │ │
│  │   Phase         │  │   Phase         │  │   Cache      │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                File System & Sandbox                        │
├─────────────────────────────────────────────────────────────┤
│                Remote Execution (Optional)                  │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

**1. Bazel Client**

- **Language**: Java
- **Role**: Command-line interface, user interaction
- **Responsibilities**:
  - Parse command-line arguments
  - Communicate with Bazel server
  - Display build progress and results
  - Handle workspace setup

**2. Bazel Server**

- **Language**: Java (primary), C++ (native components)
- **Role**: Main build orchestration engine
- **Key Subsystems**:
  - **Analysis Engine**: Builds dependency graph
  - **Execution Engine**: Runs build actions
  - **Action Cache**: Caches build results
  - **Skyframe**: Incremental evaluation framework

**3. Skyframe Framework**

- **Language**: Java
- **Purpose**: Incremental computation and caching
- **Features**:
  - Dependency tracking
  - Incremental builds
  - Parallelization
  - Error recovery

## 📦 Dependencies and Ecosystem

### Core Dependencies

**Java Ecosystem**

```txt
- Guava (Google Core Libraries)
  - Collections, utilities, concurrency
  - Version: Latest stable
  
- Protocol Buffers (protobuf)
  - Data serialization
  - RPC communication
  - Cross-language compatibility
  
- Auto-Value
  - Immutable value classes
  - Reduces boilerplate code
  
- JUnit (Testing)
  - Unit testing framework
  - Integration testing
```

**Native Dependencies**

```txt
- gRPC
  - Remote execution protocol
  - Client-server communication
  - Language: C++/Java bindings
  
- Netty
  - Asynchronous I/O
  - Network communication
  - High-performance networking
```

**Build Tools**

```txt
- Maven/Gradle (Dependency Management)
- Proguard (Code optimization)
- Error Prone (Static analysis)
- Checkstyle (Code style)
```

### External Tool Integration

**Compilers and Toolchains**

- **Java**: OpenJDK, Oracle JDK, Eclipse Compiler
- **C++**: GCC, Clang, MSVC
- **Python**: CPython, PyPy
- **Go**: Go compiler
- **Rust**: rustc
- **Android**: Android SDK, NDK

**Version Control**

- **Git**: Primary VCS support
- **Mercurial**: Limited support
- **Perforce**: Enterprise environments

## 🔨 Build Process Architecture

### Three-Phase Build Process

**1. Loading Phase**

```java
// Simplified representation
class LoadingPhase {
    // Parse WORKSPACE and BUILD files
    // Resolve external dependencies
    // Build package structures
}
```

**2. Analysis Phase**

```java
class AnalysisPhase {
    // Build dependency graph
    // Apply rules and aspects
    // Generate actions
    // Validate configurations
}
```

**3. Execution Phase**

```java
class ExecutionPhase {
    // Execute actions
    // Handle caching
    // Manage sandboxing
    // Report results
}
```

### Skyframe: The Incremental Engine

**Core Concepts**:

- **SkyValues**: Immutable computation results
- **SkyFunctions**: Pure functions that compute SkyValues
- **SkyKeys**: Unique identifiers for computations
- **Dependency Tracking**: Automatic invalidation on changes

**Benefits**:

- **Incremental**: Only recompute what changed
- **Parallel**: Independent computations run concurrently
- **Cached**: Results persist across builds
- **Consistent**: Deterministic evaluation order

## 🖥️ Platform Support

### Operating Systems

**Linux** (Primary Platform)#

- **Support Level**: Full feature support
- **Architecture**: x86_64, ARM64
- **Distributions**: Ubuntu, CentOS, Debian, Alpine
- **Special Features**: Native sandboxing, optimal performance

**macOS** (Full Support)

- **Support Level**: Complete feature parity
- **Architecture**: x86_64, Apple Silicon (ARM64)
- **Versions**: macOS 10.15+
- **Special Features**: Xcode integration, iOS development

**Windows** (Growing Support)

- **Support Level**: Most features supported
- **Architecture**: x86_64
- **Versions**: Windows 10+
- **Limitations**: Some sandboxing restrictions
- **Special Features**: MSVC integration, Windows SDK support

### Hardware Requirements

**Minimum Requirements**:

- **RAM**: 4GB (8GB recommended)
- **CPU**: Multi-core processor (4+ cores recommended)
- **Storage**: 5GB free space
- **Network**: Internet for remote repositories

**Optimal Performance**:

- **RAM**: 16GB+ for large projects
- **CPU**: 8+ cores for parallel builds
- **Storage**: SSD for faster I/O
- **Network**: High-bandwidth for remote caching

## 🌐 Remote Execution & Caching

### Remote Execution Protocol (REP)

**Technology Stack**:

- **Protocol**: gRPC-based
- **Language**: Protocol Buffers for definitions
- **Transport**: HTTP/2
- **Authentication**: Various methods (OAuth, mTLS)

**Key Components**:

```protobuf
// Simplified protocol definition
service Execution {
  rpc Execute(ExecuteRequest) returns (stream ExecuteResponse);
}

service ActionCache {
  rpc GetActionResult(GetActionResultRequest) returns (ActionResult);
  rpc UpdateActionResult(UpdateActionResultRequest) returns (ActionResult);
}

service ContentAddressableStorage {
  rpc FindMissingBlobs(FindMissingBlobsRequest) returns (FindMissingBlobsResponse);
  rpc BatchUpdateBlobs(BatchUpdateBlobsRequest) returns (BatchUpdateBlobsResponse);
}
```

### Caching Architecture

**Content-Addressable Storage (CAS)**:

- **Hashing**: SHA-256 for content addressing
- **Storage**: Distributed blob storage
- **Deduplication**: Automatic based on content hash
- **Compression**: Optional for network efficiency

**Action Cache**:

- **Key**: Action hash (inputs + command)
- **Value**: Action result (outputs + metadata)
- **TTL**: Configurable time-to-live
- **Invalidation**: Automatic on input changes

## 🔍 Performance Characteristics

### Scalability Metrics

**Build Graph Size**:

- **Small Projects**: 1K-10K targets
- **Medium Projects**: 10K-100K targets
- **Large Projects**: 100K-1M+ targets
- **Google Scale**: 10M+ targets

**Memory Usage**:

- **Base**: ~500MB for JVM overhead
- **Per Target**: ~1KB average
- **Large Builds**: 4-16GB for analysis phase
- **Optimization**: Garbage collection tuning

**Build Times**:

- **Cold Builds**: Minutes to hours (depending on size)
- **Incremental**: Seconds to minutes
- **No-op Builds**: <1 second for most projects
- **Remote Cached**: Near-instantaneous for cache hits

## 🛠️ Development Tools

### IDE Integration

**IntelliJ IDEA**:

- **Plugin**: Official Bazel plugin
- **Features**: Syntax highlighting, navigation, debugging
- **Language**: Java-based plugin

**VS Code**:

- **Extension**: Community-maintained
- **Features**: BUILD file support, task integration
- **Language**: TypeScript-based extension

**Eclipse**:

- **Plugin**: Limited community support
- **Status**: Maintenance mode

### Development Infrastructure

**Continuous Integration**:

- **BuildKite**: Primary CI system for Bazel development
- **GitHub Actions**: Community contributions
- **Jenkins**: Enterprise deployments

**Code Quality**:

- **Error Prone**: Static analysis for Java
- **Checkstyle**: Code formatting
- **SpotBugs**: Bug detection
- **Codecov**: Coverage reporting

---

*This technical foundation enables Bazel to handle builds of unprecedented
cale while maintaining performance and reliability.*
