from .app_exception_handler import AppExceptionHandler
from .generic_exception_handler import GenericExceptionHandler

ERROR_HANDLERS = [
    AppExceptionHandler(),
    GenericExceptionHandler(),
]
