# TODO List

This file tracks the progress of building a comprehensive Bazel learning repository.

## ✅ Completed Tasks

### Foundation

- [x] **Create main README with overview**
  - Create the main README.md file with repository overview, learning path, and table of contents
  
- [x] **Research and document Bazel history**
  - Create comprehensive documentation about Bazel's origins, evolution from Blaze, key milestones, and timeline
  
- [x] **Document Bazel tech stack**
  - Research and document the languages Bazel is written in, its dependencies, architecture, and technical foundation
  
- [x] **Create core concepts guide**
  - Document fundamental Bazel concepts like BUILD files, WORKSPACE, targets, rules, and the build graph

### Examples and Setup

- [x] **Add practical examples**
  - Create hands-on examples with C, C++, and Rust, plus code generation with Python/Jinja2
  
- [x] **Create devcontainer setup**
  - Set up devcontainer configuration for reproducible development environment with VS Code extensions
  
- [x] **Configure VS Code workspace**
  - Add VS Code workspace settings and extension recommendations for Bazel development

### Documentation

- [x] **Create resource collection**
  - Compile useful links, official docs, tutorials, and community resources for further learning

## 🚧 Pending Tasks

### Advanced C/C++ Integration

- [ ] **Add compile_commands.json generation**
  - Create guide for generating compile_commands.json for C/C++ IntelliSense and tooling integration
  - Show how to use Hedron's bazel-compile-commands-extractor
  - Document integration with VS Code C++ extension
  - Provide example configuration for different project structures

- [ ] **Integrate clang-tidy analysis**
  - Document how to integrate clang-tidy static analysis into Bazel builds for code quality checks
  - Show custom rules for running clang-tidy
  - Configure clang-tidy with .clang-tidy configuration file
  - Integrate with CI/CD pipeline for automated code quality checks

### Testing and Documentation

- [ ] **Add Google Test integration**
  - Show how to use Google Test (gtest) framework with Bazel for C++ unit testing
  - Create examples with cc_test rules
  - Document test discovery and execution
  - Show integration with coverage tools
  - Add examples for mocking and fixtures

- [ ] **Add Doxygen documentation generation**
  - Create example of generating Doxygen documentation using Bazel rules and custom targets
  - Show how to configure Doxygen with Bazel
  - Create custom rules for documentation generation
  - Integrate documentation building into CI/CD

### Debugging and Troubleshooting

- [ ] **Create Bazel debugging guide**
  - Document debugging techniques for Bazel builds, including build analysis, profiling, and troubleshooting
  - Cover common build failures and solutions
  - Show how to use bazel query, cquery, and aquery
  - Document performance profiling and optimization
  - Troubleshooting remote execution and caching issues

## 📋 Task Priorities

### High Priority

1. **compile_commands.json generation** - Essential for IDE support
2. **Google Test integration** - Critical for C++ development workflow
3. **Bazel debugging guide** - Helps with common issues developers face

### Medium Priority

4. **clang-tidy integration** - Important for code quality
5. **Doxygen documentation** - Useful for API documentation

## 🎯 Success Criteria

Each task should include:

- **Comprehensive documentation** with clear explanations
- **Working examples** that can be built and tested
- **Step-by-step instructions** for implementation
- **Common pitfalls and solutions**
- **Integration with existing devcontainer setup**
- **VS Code configuration** where applicable

## 📝 Notes

- All examples should focus on C, C++, and Rust (no Java)
- Examples should be reproducible using the devcontainer
- Documentation should be beginner-friendly but comprehensive
- Each advanced topic should build upon the basic examples
- Include troubleshooting sections for common issues

---

*Last updated: September 30, 2025*
