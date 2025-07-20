"""Global verbosity flag for logging"""
_verbose = False

def set_verbose(value: bool):
    global _verbose
    _verbose = bool(value)


def get_verbose() -> bool:
    return _verbose
