class ValidationError(ValueError):
    """A user-facing explanation of a rejected operation."""

class PermissionDenied(ValidationError):
    pass
