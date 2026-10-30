from django.conf import settings


def is_local() -> bool:
    """Returns True if the current environment is local."""
    return settings.ENVIRONMENT == "LOCAL"


def is_production() -> bool:
    """Returns True if the current environment is production."""
    return settings.ENVIRONMENT == "PRODUCTION"


def is_staging() -> bool:
    """Returns True if the current environment is staging."""
    return settings.ENVIRONMENT == "STAGING"


def is_testing() -> bool:
    """Returns True if the current environment is testing."""
    return settings.ENVIRONMENT == "TESTING"


def absolute_url(path: str, request=None) -> str:
    """
    The absolute URL for a site path, on SITE_URL when set (so links that
    leave the site, e.g. share text and canonical/OG tags, always use the
    public domain), otherwise on the request's own host.
    """
    if settings.SITE_URL or request is None:
        return f"{settings.SITE_URL}{path}"
    return request.build_absolute_uri(path)
