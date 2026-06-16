from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme


def safe_redirect(request, url, default="/"):
    if url and url_has_allowed_host_and_scheme(
        url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(url)
    return redirect(default)


def parse_quantity(raw, default=1):
    try:
        return max(1, int(raw))
    except (TypeError, ValueError):
        return default


def parse_cart_quantity(raw, default=1):
    """Cart update quantity — 0 means remove item."""
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default
