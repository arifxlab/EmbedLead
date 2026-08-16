class AppError(Exception):
    """Base exception for application-level errors."""


class WidgetNotFoundError(AppError):
    """Raised when a widget cannot be found."""


class WidgetInactiveError(AppError):
    """Raised when a widget exists but is inactive."""


class LeadNotFoundError(AppError):
    """Raised when a lead cannot be found."""
