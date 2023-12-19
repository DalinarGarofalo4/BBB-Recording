import pytest
from unittest.mock import patch
from requests import Response

from starlette.status import (
    HTTP_201_CREATED,
    HTTP_405_METHOD_NOT_ALLOWED
)

from app.api.schemas.auth_schema import XBearerSchema
from app.api.schemas.webdav_schema import (
    WebDAVRequestInput,
    WebDAVCreateFolderDTO,
    WebDAVGetFileDTO,
    WebDAVUploadFileDTO
)
from app.api.services.web_dav_service import WebDAVService
from app.config import current
from app.exceptions import ApiException


@pytest.mark.asyncio
async def test_configure_webdav_client_ok():
    webdav_service = WebDAVService()
    user = 'fake-user'
    token = 'fake-token'
    await webdav_service.configure_webdav_client(x_bearer_schema=XBearerSchema(user=user, token=token))

    assert webdav_service._username == user
    assert webdav_service._base_user_url == f'{current.NEXT_CLOUD.API_URL}/{current.NEXT_CLOUD.WEBDAV_API}/files/{user}'
    assert webdav_service._headers == {'Authorization': f'Bearer {token}'}


@pytest.mark.asyncio
@patch('app.api.services.web_dav_service.WebDAVService._send_request')
async def test_create_folder_200(send_request_mock):
    send_request_mock.return_value = Response()
    send_request_mock.return_value.status_code = HTTP_201_CREATED

    webdav_service = WebDAVService()
    await webdav_service.configure_webdav_client(x_bearer_schema=XBearerSchema(
        user='fake-user', token='fake-token'
    ))

    status = await webdav_service.create_folder(create_folder_dto=WebDAVCreateFolderDTO(folder_name='fake_folder'))

    assert status == HTTP_201_CREATED


@pytest.mark.asyncio
@patch('app.api.services.web_dav_service.WebDAVService._send_request')
async def test_create_folder_405(send_request_mock):
    send_request_mock.return_value = Response()
    send_request_mock.return_value.status_code = HTTP_405_METHOD_NOT_ALLOWED

    webdav_service = WebDAVService()
    await webdav_service.configure_webdav_client(x_bearer_schema=XBearerSchema(
        user='fake-user', token='fake-token'
    ))

    status = await webdav_service.create_folder(create_folder_dto=WebDAVCreateFolderDTO(folder_name='fake_folder'))

    assert status == HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_status', [400, 422, 503, 504])
@patch('app.api.services.web_dav_service.WebDAVService._send_request')
async def test_create_folder_raise_exception(send_request_mock, expected_status):
    send_request_mock.side_effect = ApiException(expected_status)

    webdav_service = WebDAVService()
    await webdav_service.configure_webdav_client(x_bearer_schema=XBearerSchema(
        user='fake-user', token='fake-token'
    ))

    with pytest.raises(ApiException) as ex:
        await webdav_service.create_folder(create_folder_dto=WebDAVCreateFolderDTO(folder_name='fake_folder'))

    assert ex.value.code == expected_status  # pylint: disable=E1101


@pytest.mark.asyncio
@patch('app.api.services.web_dav_service.WebDAVService._send_request')
async def test_get_file_200(send_request_mock):
    response = Response()
    response._content = b'fake-file'
    response.status_code = 200
    send_request_mock.return_value = response

    webdav_service = WebDAVService()
    await webdav_service.configure_webdav_client(x_bearer_schema=XBearerSchema(
        user='fake-user', token='fake-token'
    ))

    file_name, file = await webdav_service.get_file(
        get_file_dto=WebDAVGetFileDTO(file_url='https://example.com/ExampleMeet/ExampleMeet-70342.mp4')
    )

    assert file_name == 'ExampleMeet-70342.mp4'
    assert file == b'fake-file'


@pytest.mark.asyncio
@patch('app.api.services.web_dav_service.WebDAVService._send_request')
async def test_get_file_200(send_request_mock):
    response = Response()
    response.status_code = 404
    send_request_mock.return_value = response

    webdav_service = WebDAVService()
    await webdav_service.configure_webdav_client(x_bearer_schema=XBearerSchema(
        user='fake-user', token='fake-token'
    ))

    with pytest.raises(ApiException) as ex:
        await webdav_service.get_file(
            get_file_dto=WebDAVGetFileDTO(file_url='https://example.com/ExampleMeet/ExampleMeet-70342.mp4')
        )

    assert ex.value.code == 404  # pylint: disable=E1101
    assert ex.value.message == 'Not Found'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'file:not-found'

@pytest.mark.asyncio
@patch('app.api.services.web_dav_service.WebDAVService._send_request')
async def test_upload_file_200(send_request_mock):
    send_request_mock.return_value = Response()
    send_request_mock.return_value.status_code = HTTP_201_CREATED

    webdav_service = WebDAVService()
    await webdav_service.configure_webdav_client(x_bearer_schema=XBearerSchema(
        user='fake-user', token='fake-token'
    ))

    status = await webdav_service.upload_file(
        upload_file_dto=WebDAVUploadFileDTO(
            file_name='fake_file_name', file=b'fake_file', full_folder_path='folder_1/folder_2/folder_3'
        )
    )

    assert status == HTTP_201_CREATED


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_status', [400, 422, 503, 504])
@patch('app.api.services.web_dav_service.WebDAVService._send_request')
async def test_upload_file_raise_exception(send_request_mock, expected_status):
    send_request_mock.side_effect = ApiException(expected_status)

    webdav_service = WebDAVService()
    await webdav_service.configure_webdav_client(x_bearer_schema=XBearerSchema(
        user='fake-user', token='fake-token'
    ))

    with pytest.raises(ApiException) as ex:
        await webdav_service.upload_file(
            upload_file_dto=WebDAVUploadFileDTO(
                file_name='fake_file_name', file=b'fake_file', full_folder_path='folder_1/folder_2/folder_3'
            )
        )

    assert ex.value.code == expected_status  # pylint: disable=E1101


@pytest.mark.asyncio
async def test_send_request_400():
    webdav_service = WebDAVService()
    await webdav_service.configure_webdav_client(x_bearer_schema=XBearerSchema(
        user='fake-user', token='fake-token'
    ))

    with pytest.raises(ApiException) as ex:
        await webdav_service._send_request(webdav_request_input=WebDAVRequestInput(
            method='fake-method', url='fake-url',
        ))

    assert ex.value.code == 400  # pylint: disable=E1101
    assert ex.value.message == 'Bad Request. Method not allowed'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'webdav:method-not-allowed'
