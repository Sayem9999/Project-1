# Known Issues & Development Pitfalls

This document serves as a checklist of errors encountered during development and best practices to avoid repeating them.

## 🚨 Critical Environment Warnings

### 1. Python Version Incompatibility
- **Issue**: Python **3.14.x** (and potentially 3.13+) introduces changes to the `typing` module and C-API that break current versions of **SQLAlchemy** (specifically `orm.decl_base`).
- **Error Seen**: `TypeError: descriptor '__getitem__' requires a 'typing.Union' object but received a 'tuple'`.
- **Solution**: Strictly use **Python 3.11** or **3.12** for this project until all dependencies verify support for newer versions.

### 2. External Binaries (FFmpeg)
- **Issue**: `ffmpeg` and `ffprobe` may not be in the system `PATH` on all developer machines or deployment environments.
- **Error Seen**: `FileNotFoundError` or silent failures/stalls in media processing agents.
- **Solution**:
    - Always implement a **path resolution helper** (like `_resolve_path` in `media_analysis.py`).
    - Check the `tools/` directory for local binaries if the system command fails.
    - Log explicit errors if binaries are missing at startup.

## 🛠️ Coding Best Practices

### 3. Path Handling
- **Issue**: Hardcoding paths like `"backend/app"` assumes the command is run from a specific directory (e.g., project root).
- **Error Seen**: `FileNotFoundError` or empty results when running scripts from `backend/` or other subdirectories.
- **Solution**:
    - Use `pathlib.Path(__file__).parent` to resolve paths relative to the current module.
    - Avoid `os.getcwd()` for locating project files.
    - Example:
      ```python
      # BAD
      scan("backend/app")
      
      # GOOD
      root_dir = Path(__file__).parent.parent.absolute()
      scan(str(root_dir))
      ```

### 4. Async & Blocking Operations
- **Issue**: Running heavy CPU-bound tasks (like `scenedetect` or `ffmpeg`) directly in an `async` function blocks the event loop.
- **Error Seen**: The API becomes unresponsive ("stalls") during video processing; health checks fail.
- **Solution**:
    - Always wrap blocking CPU calls in `await asyncio.to_thread(...)`.
    - Set explicit timeouts using `asyncio.wait_for`.
    - Add granular logs *before* and *after* the blocking call to trace stalls.

### 5. SQLAlchemy & Typing
- **Issue**: Complex type hints in Pydantic/SQLAlchemy models can conflict with runtime inspection in newer Python versions.
- **Solution**: Use `typing.Optional` instead of `| None` in SQLAlchemy models if encountering issues, and ensure `ForwardRef`s are handled correctly.

## ✅ Pre-Commit Checklist
- [ ] Check active Python version (`python --version`).
- [ ] Verify `ffmpeg` is accessible or correctly configured in `tools/`.
- [ ] Run `verify_introspection.py` to ensure file paths are resolving correctly.
- [ ] Ensure no hardcoded relative paths exist in new services.
