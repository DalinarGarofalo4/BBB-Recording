from http.client import responses
import os
from typing import Tuple

from enum import Enum
from requests import exceptions, request, Response
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_504_GATEWAY_TIMEOUT
)

from app.api.schemas.webdav_schema import (
    WebDAVRequestInput,
    WebDAVCreateFolderDTO,
    WebDAVGetFileDTO,
    WebDAVUploadFileDTO
)
from app.api.schemas.auth_schema import XBearerSchema
from app.error_codes import (
    FILE_NOT_FOUND,
    WEBDAV_CLIENT_ERROR,
    WEBDAV_METHOD_NOT_ALLOWED,
    WEBDAV_SERVER_ERROR,
    WEBDAV_TIMEOUT_ERROR,
)
from app.exceptions import ApiException, raise_exception
from app.config import current


class WebDAVHTTPMethod(Enum):
    POST = 'POST'
    PUT = 'PUT'
    GET = 'GET'
    DELETE = 'DELETE'
    MKCOL = 'MKCOL'
    PROPFIND = 'PROPFIND'
    MOVE = 'MOVE'
    COPY = 'COPY'
    REPORT = 'REPORT'


class WebDAVService:

    def __init__(self):
        self._username = None
        self._base_user_url = None
        self._headers = {}

    async def configure_webdav_client(self, x_bearer_schema: XBearerSchema) -> None:
        """
        Init WebDAV service...
        :param x_bearer_schema:
        :return:
        """
        self._username = x_bearer_schema.user
        self._base_user_url = f'{current.NEXT_CLOUD.API_URL}/{current.NEXT_CLOUD.WEBDAV_API}/files/{self._username}'
        self._headers = {'Authorization': f'Bearer {x_bearer_schema.token}'}

    async def create_folder(self, create_folder_dto: WebDAVCreateFolderDTO) -> int:
        url = f'{self._base_user_url}/{create_folder_dto.folder_name}'
        webdav_request_input = WebDAVRequestInput(
            method=WebDAVHTTPMethod.MKCOL.value, url=url, headers=self._headers
        )
        response = await self._send_request(webdav_request_input)
        return response.status_code

    async def get_file(self, get_file_dto: WebDAVGetFileDTO) -> Tuple[str, bytes]:
        file_url = get_file_dto.file_url
        file_name = os.path.basename(file_url)
        webdav_request_input = WebDAVRequestInput(
            method=WebDAVHTTPMethod.GET.value, url=file_url, headers=self._headers
        )
        response = await self._send_request(webdav_request_input)
        if response.status_code == HTTP_404_NOT_FOUND:
            raise_exception(ApiException(), HTTP_404_NOT_FOUND, responses[HTTP_404_NOT_FOUND], FILE_NOT_FOUND)
        return file_name, response.content

    async def upload_file(self, upload_file_dto: WebDAVUploadFileDTO):
        file_name = upload_file_dto.file_name
        file = upload_file_dto.file
        full_folder_path = upload_file_dto.full_folder_path

        user_drive_url = f'{self._base_user_url}/{full_folder_path}/{file_name}'

        webdav_request_input = WebDAVRequestInput(
            method=WebDAVHTTPMethod.PUT.value, url=user_drive_url, headers=self._headers, body=file
        )

        response = await self._send_request(webdav_request_input)
        return response.status_code

    @staticmethod
    async def _send_request(webdav_request_input: WebDAVRequestInput) -> Response:
        response: Response = Response()
        try:
            method = webdav_request_input.method
            url = webdav_request_input.url
            headers = webdav_request_input.headers
            body = webdav_request_input.body

            if method not in list(map(lambda x: x.value, WebDAVHTTPMethod)):
                msg = f'{responses[HTTP_400_BAD_REQUEST]}. Method not allowed'
                raise_exception(ApiException(), HTTP_400_BAD_REQUEST, msg, WEBDAV_METHOD_NOT_ALLOWED)

            response = request(method=method.__str__(), url=url, data=body, headers=headers, stream=True)

        except exceptions.Timeout as ex:
            msg = f'{responses[HTTP_504_GATEWAY_TIMEOUT]}'
            raise_exception(ApiException(), HTTP_504_GATEWAY_TIMEOUT, msg, WEBDAV_TIMEOUT_ERROR, ex)

        except exceptions.HTTPError as ex:
            status = ex.response.status_code \
                if ex.response is not None and hasattr(ex.response, 'status_code') else HTTP_400_BAD_REQUEST

            error_code = WEBDAV_CLIENT_ERROR \
                if HTTP_400_BAD_REQUEST <= status < HTTP_500_INTERNAL_SERVER_ERROR else WEBDAV_SERVER_ERROR
            raise_exception(ApiException(), status, responses[status], error_code, ex)

        except exceptions.ConnectionError as ex:
            msg = f'{responses[HTTP_404_NOT_FOUND]}. The url provided cannot be accessed. error: {str(ex)}'
            raise_exception(ApiException(), HTTP_404_NOT_FOUND, msg, None, ex)

        except ApiException as ex:
            raise ex
        except Exception as ex:
            msg = f'{responses[HTTP_422_UNPROCESSABLE_ENTITY]}'
            raise_exception(ApiException(), HTTP_422_UNPROCESSABLE_ENTITY, msg, None, ex)

        return response
