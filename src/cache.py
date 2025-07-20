"""Simple in-memory cache utilities used for tests."""

_accounts = []
_posts = []

def get_accounts():
    return _accounts


def add_post(post):
    _posts.append(post)


def get_posts():
    return list(_posts)
