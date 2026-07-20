from notbehomeless.models.website import Website


class AppException(Exception):
    def __init__(
            self,
            message: str,
            status_code: int = 500,
            website: Website | None = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.website = website
