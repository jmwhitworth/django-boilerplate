class ApplicationError(Exception):
    """
    Raised by services/selectors for business-rule violations, as opposed to
    programmer errors (AssertionError) or Django's own ValidationError.

    `extra` can carry structured, field-level detail for callers that want to
    surface more than the top-level message (e.g. a form or an API response).
    """

    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}
