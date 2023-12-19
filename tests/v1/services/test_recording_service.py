import pytest
from unittest.mock import patch
from requests import Response

from starlette.status import (
    HTTP_201_CREATED,
    HTTP_405_METHOD_NOT_ALLOWED
)

from app.api.schemas.auth_schema import XBearerSchema
from app.api.services.recording_service import RecordingService
from app.api.services.web_dav_service import WebDAVService


@pytest.mark.asyncio
@pytest.mark.parametrize('folder_path, result', [
    ('', ''),
    ('///', ''),
    ('folder_1', 'folder_1'),
    ('folder_1/folder_2', 'folder_1/folder_2'),
    ('folder_1/folder_2/folder_3', 'folder_1/folder_2/folder_3'),
    ('folder_1///folder_2///folder_3///', 'folder_1/folder_2/folder_3'),
])
@patch('app.api.services.web_dav_service.WebDAVService._send_request')
async def test_create_full_folder_path(send_request_mock, folder_path, result):
    send_request_mock.return_value = Response()
    send_request_mock.return_value.status_code = HTTP_201_CREATED

    webdav_service = WebDAVService()
    await webdav_service.configure_webdav_client(x_bearer_schema=XBearerSchema(
        user='fake-user', token='fake-token'
    ))
    recording_service = RecordingService(webdav_service=webdav_service)

    path = await recording_service.create_full_folder_path(folder_path)
    assert path == result
