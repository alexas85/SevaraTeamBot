"""Regression test: ensure handlers.admin can be imported without circular-import errors."""
import importlib
import sys


def test_admin_handler_import_is_not_circular():
    # Remove cached modules so the import is exercised fresh.
    for key in list(sys.modules.keys()):
        if key in ("handlers.admin", "handlers", "config"):
            del sys.modules[key]

    # This must not raise ImportError due to a circular dependency on `main`.
    mod = importlib.import_module("handlers.admin")
    assert hasattr(mod, "register_admin_handlers")


if __name__ == "__main__":
    test_admin_handler_import_is_not_circular()
    print("OK")
