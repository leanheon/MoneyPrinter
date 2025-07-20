"""Simple in-memory cache utilities used for tests."""

_accounts = {}
_posts = []


def get_accounts(platform: str):
    """Return cached account configs for a platform."""
    return _accounts.get(platform, [])


def add_account(platform: str, account: dict):
    _accounts.setdefault(platform, []).append(account)


def add_post(platform: str, post: dict):
    """Store a posted item in the cache."""
    _posts.append({"platform": platform, "post": post})


def get_posts(platform: str | None = None):
    """Return posts, optionally filtered by platform."""
    if platform is None:
        return list(_posts)
    return [p for p in _posts if p["platform"] == platform]
