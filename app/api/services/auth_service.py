from jose import JWTError, jwt
import json
from json import JSONDecodeError
from http.client import responses
import logging

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)

from app.api.schemas.auth_schema import XBearerSchema
from app.config import current
from app.exceptions import ApiException, raise_exception
from app.error_codes import (
    AUTH_TOKEN_INVALID,
    USER_INVALID_CREDENTIALS
)

LOGGER = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthService:

    @staticmethod
    async def verify_access_token(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, current.JWT.SECRET_KEY, algorithms=current.JWT.ALGORITHM)
            return payload
        except JWTError as ex:
            msg = f'{responses[HTTP_401_UNAUTHORIZED]}. Authorization error: {str(ex)}. Could not validate credentials'
            raise_exception(
                ApiException(), HTTP_401_UNAUTHORIZED, msg, AUTH_TOKEN_INVALID, ex
            )

    @staticmethod
    async def parse_x_bearer(x_bearer: str) -> XBearerSchema:
        # TODO: decrypt x_bearer here...

        parsed_x_bearer = {}
        try:
            parsed_x_bearer = json.loads(x_bearer)
        except JSONDecodeError as ex:
            msg = f'{responses[HTTP_400_BAD_REQUEST]}. Incorrect X-BEARER.'
            raise_exception(ApiException(), HTTP_400_BAD_REQUEST, msg, USER_INVALID_CREDENTIALS, ex)

        user = parsed_x_bearer.get('user', None)
        token = parsed_x_bearer.get('token', None)
        if user in [None, ''] or token in [None, '']:
            msg = f'{responses[HTTP_400_BAD_REQUEST]}. Incorrect X-BEARER.'
            raise_exception(ApiException(), HTTP_400_BAD_REQUEST, msg, USER_INVALID_CREDENTIALS)
        return XBearerSchema(user=user, token=token)
