# VS Code Configuration

This directory contains VS Code-specific configuration for optimal Bazel development experience.

## 📁 Files Overview

### `settings.json`
**Workspace-specific settings** that optimize VS Code for Bazel development:

- **Bazel Integration**: Buildifier path, query sharing, CodeLens
- **File Associations**: `.bzl`, `BUILD`, `WORKSPACE` files mapped to Starlark
- **Language Configs**: C/C++, Rust, Python optimizations
- **Performance**: Exclusions for Bazel output directories
- **Editor**: Format on save, rulers, tab settings

### `extensions.json`
**Recommended extensions** for Bazel development:

- **Essential**: Bazel, C/C++, Rust Analyzer, Python
- **Helpful**: GitLens, GitHub Copilot, YAML support
- **Quality**: Spell checker, formatters, linters

### `tasks.json`
**Pre-configured tasks** for common Bazel operations:

```
Ctrl+Shift+P → "Tasks: Run Task" → Select task
```

**Available tasks:**
- `Bazel: Build All` - Build entire project
- `Bazel: Test All` - Run all tests
- `Bazel: Clean` - Clean build outputs
- `C: Build Hello C` - Build C example
- `C++: Build Hello C++` - Build C++ example
- `Rust: Build Hello Rust` - Build Rust example
- `Buildifier: Format All` - Format all Bazel files

### `launch.json`
**Debug configurations** for different languages:

```
F5 or Run → Start Debugging → Select configuration
```

**Available configurations:**
- `Debug C Application` - Debug C examples with GDB
- `Debug C++ Application` - Debug C++ examples with GDB
- `Debug Rust Application` - Debug Rust examples with LLDB
- `Debug CodeGen Apps` - Debug generated code examples

## 🚀 Quick Setup

### 1. Install Recommended Extensions
```bash
# VS Code will prompt to install recommended extensions
# Or manually: Ctrl+Shift+P → "Extensions: Show Recommended Extensions"
```

### 2. Verify Bazel Integration
- Open any `BUILD` file
- Should see syntax highlighting
- CodeLens should show "Build" and "Test" options

### 3. Test Build Tasks
- `Ctrl+Shift+P` → "Tasks: Run Task"
- Select "Bazel: Build All"
- Should build successfully

## ⚙️ Customization

### Adding New Tasks
Edit `tasks.json` to add project-specific tasks:

```json
{
    "label": "My Custom Task",
    "type": "shell",
    "command": "bazel",
    "args": ["build", "//my/target:name"],
    "group": "build"
}
```

### Debug Configuration
Add new debug configurations in `launch.json`:

```json
{
    "name": "Debug My App",
    "type": "cppdbg",
    "request": "launch",
    "program": "${workspaceFolder}/bazel-bin/my/app",
    "preLaunchTask": "Build My App"
}
```

### Language-Specific Settings
Modify `settings.json` for your preferences:

```json
{
    "rust-analyzer.cargo.features": ["my-feature"],
    "C_Cpp.default.cppStandard": "c++20",
    "python.defaultInterpreterPath": "/custom/path/python"
}
```

## 🐛 Troubleshooting

### Bazel Extension Not Working
1. **Check Buildifier**: `which buildifier`
2. **Verify Bazel**: `bazel version`
3. **Reload Window**: `Ctrl+Shift+P` → "Developer: Reload Window"

### IntelliSense Issues
1. **C/C++**: Check `C_Cpp.default.compilerPath` in settings
2. **Rust**: Ensure `rust-analyzer` extension is installed
3. **Python**: Verify Python interpreter path

### Performance Issues
1. **Exclude Bazel dirs**: Already configured in settings
2. **Increase memory**: VS Code settings → Search "memory"
3. **Disable unused extensions**: Extension view → Disable

### Task Failures
1. **Check working directory**: Tasks run from workspace root
2. **Verify paths**: Ensure target paths are correct
3. **Check terminal**: View task output in terminal

## 📚 Keyboard Shortcuts

### Essential Shortcuts
- `Ctrl+Shift+P` - Command palette
- `F5` - Start debugging
- `Ctrl+Shift+`` - New terminal
- `Ctrl+K Ctrl+T` - Select color theme

### Bazel-Specific (via Command Palette)
- "Bazel: Build Target" - Build specific target
- "Bazel: Test Target" - Test specific target
- "Bazel: Clean" - Clean workspace

### Custom Shortcuts
Add to `keybindings.json` for frequent tasks:

```json
[
    {
        "key": "ctrl+shift+b",
        "command": "workbench.action.tasks.runTask",
        "args": "Bazel: Build All"
    }
]
```

---

*This configuration provides a productive development environment tailored specifically for Bazel projects with C, C++, and Rust.*