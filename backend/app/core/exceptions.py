class AppException(Exception):
    def __init__(self, message: str, code: str, status_code: int):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(AppException):
    def __init__(self, message="The email or password you entered is incorrect."):
        super().__init__(message=message, code="INVALID_CREDENTIALS", status_code=401)

class ForbiddenError(AppException):
    def __init__(self, message="You do not have permission to perform this action."):
        super().__init__(message=message, code="FORBIDDEN", status_code=403)

class NotFoundError(AppException):
    def __init__(self, message="The requested resource was not found."):
        super().__init__(message=message, code="NOT_FOUND", status_code=404)

class ValidationError(AppException):
    def __init__(self, message="The request data is invalid."):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422)

class DocumentProcessingError(AppException):
    def __init__(self, message="Failed to process the document."):
        super().__init__(message=message, code="DOCUMENT_PROCESSING_FAILED", status_code=500)

class LLMError(AppException):
    def __init__(self, message="The language model service is currently unavailable."):
        super().__init__(message=message, code="LLM_UNAVAILABLE", status_code=502)
