from typing import Optional

from .base_schema import ResponseBase


class ApiExceptionResponse(ResponseBase):
    message: Optional[str]
    error_code: Optional[str]
    subtype: Optional[str]
