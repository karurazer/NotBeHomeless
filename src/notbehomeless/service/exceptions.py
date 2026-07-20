"""Service-layer exceptions."""
from notbehomeless.models.base_exception import AppException
from notbehomeless.models.website import Website


class AutoSignerAlreadyRunning(AppException):
    """An auto-signer is already running for the site."""

    def __init__(self, site: Website):
        super().__init__(
            f"Auto-signer for {site.value} is already running",
            status_code=409,
            website=site,
        )


class AutoSignerNotRunning(AppException):
    """No auto-signer is running for the site."""

    def __init__(self, site: Website):
        super().__init__(
            f"Auto-signer for {site.value} is not running",
            status_code=404,
            website=site,
        )
