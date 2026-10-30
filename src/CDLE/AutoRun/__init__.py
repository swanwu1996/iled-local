"""Keep iLED's native generator and normalize its generated script header."""

import importlib.util as _importlib_util
import os as _os
from pathlib import Path as _Path
import sys as _sys
import tempfile as _tempfile
import types as _types
from functools import wraps as _wraps


def _native_module():
    name = "_iled_autorun_native.AutoRun"
    cached = _sys.modules.get(name)
    if cached is not None:
        return cached
    native_paths = list(_Path(__file__).resolve().parent.parent.glob("AutoRun.*.so"))
    if len(native_paths) != 1:
        raise ImportError("Expected exactly one native iLED AutoRun extension")
    namespace = _types.ModuleType("_iled_autorun_native")
    namespace.__path__ = []
    _sys.modules.setdefault(namespace.__name__, namespace)
    spec = _importlib_util.spec_from_file_location(name, native_paths[0])
    if spec is None or spec.loader is None:
        raise ImportError("Cannot load the native iLED AutoRun extension")
    module = _importlib_util.module_from_spec(spec)
    _sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        _sys.modules.pop(name, None)
        raise
    return module


def _normalize_script(path):
    if not path.is_file():
        return
    data = path.read_bytes()
    if data.startswith(b"\\\n#!"):
        fixed = data[2:]
    elif data.startswith(b"\\\r\n#!"):
        fixed = data[3:]
    else:
        return
    mode = path.stat().st_mode & 0o777
    fd, temporary = _tempfile.mkstemp(prefix=".iled-script-", dir=path.parent)
    try:
        with _os.fdopen(fd, "wb") as stream:
            stream.write(fixed)
            stream.flush()
            _os.fsync(stream.fileno())
        _os.chmod(temporary, mode)
        _os.replace(temporary, path)
    finally:
        if _os.path.exists(temporary):
            _os.unlink(temporary)


def _fixed_writer(original):
    @_wraps(original)
    def write(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        _normalize_script(_Path(self.cwd) / "submit_job.sh")
        return result

    write._iled_script_header_fixed = True
    return write


_native = _native_module()
for _name, _value in vars(_native).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

for _name in dir(AutoRun):
    if _name.startswith("write_") and "jobfile" in _name:
        _writer = getattr(AutoRun, _name)
        if not getattr(_writer, "_iled_script_header_fixed", False):
            setattr(AutoRun, _name, _fixed_writer(_writer))

__doc__ = _native.__doc__
