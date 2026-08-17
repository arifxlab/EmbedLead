class AppError(Exception):
    """Base exception for application-level errors."""


class WidgetNotFoundError(AppError):
    """Raised when a widget cannot be found."""


class WidgetInactiveError(AppError):
    """Raised when a widget exists but is inactive."""


class LeadNotFoundError(AppError):
    """Raised when a lead cannot be found."""


class UserAlreadyExistsError(AppError):
    """Raised when attempting to create a user with an existing email."""


class InvalidCredentialsError(AppError):
    """Raised when authentication credentials are invalid."""
