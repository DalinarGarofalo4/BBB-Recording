import logging
from http.client import responses
from typing import TypeVar, List, Union, Type, Dict, Optional, Callable, Any, Coroutine

from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


LOGGER = logging.getLogger(__name__)

_ET = TypeVar('_ET', bound=Exception)


class ApiException(Exception):
    """
    Generic Error
    """

    def __init__(
            self,
            status: int = 500,
            message: str = 'An unhandled exception occurred',
            details: Optional[Union[str, Dict[str, List[str]]]] = None,
            subtype: Optional[str] = None,
            error_code: Optional[str] = None,
            resp_headers: Optional[Dict[str, Union[str, int]]] = None,
            *args,
    ) -> None:
        super(ApiException, self).__init__(*args)

        self.code = status
        self.message = message
        self.details = details
        self.type = 'ErrorResponse'
        self.subtype = subtype
        self.error_code = error_code
        self.resp_headers = resp_headers

    def __call__(self, *args, **kwargs):
        return self(*args, **kwargs)


def raise_exception(
        exception_type: _ET,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        exception: Optional[Exception] = None
) -> None:
    msg = f"STATUS_CODE: {status_code}. MESSAGE: {message}"

    if error_code is not None:
        msg = f"{msg}. ErrorCode: {error_code}"

    if exception is not None:
        msg = f"{msg}. Exception: {str(exception)}"

    LOGGER.exception(msg)
    params = {
        'status': status_code,
        'message': message,
        'subtype': error_code
    }
    raise exception_type.__class__(**params)


def _get_default_handler(
    status_code: int,
    exc_class: Type[ValidationError],
    jsonable_encoder
) -> Callable[[Request, Any], Coroutine[Any, Any, JSONResponse]]:
    async def validation_error_handler(request: Request, exc: exc_class) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                'code': status_code,
                'message': responses[status_code],
                'type': 'ErrorResponse',
                'details': jsonable_encoder(exc.errors()),  # type: ignore[attr-defined]
            },
        )

    return validation_error_handler


def set_exception_handlers(
    app: Starlette,
    jsonable_encoder,
    exc_for_default_handler: Optional[
        Dict[
            Type[ValidationError],
            int
        ]] = None,
) -> None:
    if exc_for_default_handler is None:
        exc_for_default_handler = {}
    exc_for_default_handler.setdefault(ValidationError, HTTP_422_UNPROCESSABLE_ENTITY)

    @app.exception_handler(ApiException)
    async def api_exception_handler(request: Request, exc: ApiException) -> JSONResponse:
        headers = getattr(exc, 'headers', None)
        json_resp = {
            'code': exc.code,
            'message': exc.message,
            'type': exc.type,
            'error_code': exc.error_code,
        }
        if exc.subtype:
            json_resp['subtype'] = exc.subtype

        return JSONResponse(
            status_code=exc.code,
            content=json_resp,
            headers=headers,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        headers = getattr(exc, 'headers', None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                'code': exc.status_code,
                'message': responses[exc.status_code],
                'type': 'ErrorResponse',
                'detail': exc.detail
            },
            headers=headers,
        )

    @app.exception_handler(Exception)
    async def exception_error_handler(request: Request, exc: Exception) -> JSONResponse:
        msg = f"STATUS_CODE: {HTTP_500_INTERNAL_SERVER_ERROR}. MESSAGE: {responses[HTTP_500_INTERNAL_SERVER_ERROR]}"
        LOGGER.exception(f"{msg}. Exception: {str(exc)}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'code': HTTP_500_INTERNAL_SERVER_ERROR,
                'message': responses[HTTP_500_INTERNAL_SERVER_ERROR],
                'type': 'ErrorResponse',
            },
        )

    for key, value in exc_for_default_handler.items():
        app.add_exception_handler(key, _get_default_handler(value, key, jsonable_encoder))