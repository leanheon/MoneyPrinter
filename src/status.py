"""Utility functions for global status flags."""

_verbose = False


def set_verbose(value: bool) -> None:
    global _verbose
    _verbose = bool(value)


def get_verbose() -> bool:
    return _verbose
