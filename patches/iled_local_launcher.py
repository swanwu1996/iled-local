"""Local iLED entry point with activation gating disabled for this process."""

from functools import wraps


def _allow_module(module: str) -> None:
    return None


def _install_activation_override(entry):
    loader = entry._load_runtime_guard
    if getattr(loader, "_iled_local_launcher", False):
        return

    @wraps(loader)
    def load_guard():
        guard = loader()
        guard.require_activation = _allow_module
        return guard

    load_guard._iled_local_launcher = True
    entry._load_runtime_guard = load_guard


def main():
    import iled_main

    _install_activation_override(iled_main)
    return iled_main.main()


if __name__ == "__main__":
    raise SystemExit(main())
