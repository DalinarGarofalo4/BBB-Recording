import pytest
from unittest.mock import patch

from app.exceptions import ApiException
from app.utils.recording_util import get_full_folder_path
from app.utils.file_util import create_folder
from app.utils.rsa_util import decrypt, encrypt


@pytest.mark.asyncio
@pytest.mark.parametrize('folder_path, result', [
    ("", []),
    ("///", []),
    ("folder_1", ["folder_1"]),
    ("folder_1/folder_2", ["folder_1", "folder_1/folder_2"]),
    ("folder_1/folder_2/folder_3", ["folder_1", "folder_1/folder_2", "folder_1/folder_2/folder_3"]),
    ("folder_1///folder_2///folder_3///", ["folder_1", "folder_1/folder_2", "folder_1/folder_2/folder_3"]),
])
async def test_get_full_folder_path(folder_path: str, result: list):
    assert result == await get_full_folder_path(folder_path)


@pytest.mark.asyncio
@patch('os.makedirs')
async def test_create_folder_success(make_dirs_mock):
    make_dirs_mock.return_value = None
    path = 'path/to/folder'

    await create_folder(path)
    make_dirs_mock.assert_called_once_with(path)


@pytest.mark.asyncio
@patch('os.makedirs')
async def test_create_folder_409(make_dirs_mock):
    make_dirs_mock.side_effect = OSError('Permission denied')

    with pytest.raises(ApiException) as ex:
        await create_folder(path='path/to/folder')

    assert ex.value.code == 409  # pylint: disable=E1101
    assert ex.value.message == 'Conflict. Folder creation failed'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'folder:creation-failed'


@pytest.mark.asyncio
@pytest.mark.parametrize('message', [
    "example message",
    '{"field_1": "example_field_1", "field_2": "example_field_2"}',
])
@patch('app.utils.rsa_util._get_public_key')
@patch('app.utils.rsa_util._get_private_key')
async def test_rsa_encrypt_decrypt_message_ok(
    _get_private_key_mock, _get_public_key_mock, message, get_fake_public_key, get_fake_private_key
):
    _get_private_key_mock.return_value = get_fake_private_key
    _get_public_key_mock.return_value = get_fake_public_key

    encrypted_message = await encrypt(message)
    decrypted_message = await decrypt(encrypted_message)

    assert decrypted_message == message


@pytest.mark.asyncio
@pytest.mark.parametrize('message', [
    "example message",
    "{'field_1': 'example_field_1', 'field_2': 'example_field_2'}",
])
@patch('app.utils.rsa_util._get_key')
@patch('app.utils.rsa_util._get_public_key')
async def test_rsa_encrypt_message_fail_incorrect_public_key(
    _get_public_key_mock, get_key_mock, message
):
    _get_public_key_mock.return_value = None

    get_key_mock.return_value = None
    with pytest.raises(ApiException) as ex:
        await encrypt(message)

    assert ex.value.code == 400  # pylint: disable=E1101
    assert ex.value.message == 'Bad Request. Encrypt process failed'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'rsa:encrypt-process-fail'


@pytest.mark.asyncio
@pytest.mark.parametrize('message', [
    123, True, False
])
@patch('app.utils.rsa_util._get_public_key')
async def test_rsa_encrypt_message_fail_incorrect_message(_get_public_key_mock, message, get_fake_public_key):
    _get_public_key_mock.return_value = get_fake_public_key

    with pytest.raises(ApiException) as ex:
        await encrypt(message)

    assert ex.value.code == 400  # pylint: disable=E1101
    assert ex.value.message == 'Bad Request. Encrypt process failed'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'rsa:encrypt-process-fail'


@pytest.mark.asyncio
@pytest.mark.parametrize('message', [
    "example message",
    "{'field_1': 'example_field_1', 'field_2': 'example_field_2'}",
])
@patch('app.utils.rsa_util._get_key')
@patch('app.utils.rsa_util._get_private_key')
async def test_rsa_decrypt_message_fail_incorrect_public_key(
    _get_private_key_mock, get_key_mock, message, get_fake_private_key
):
    _get_private_key_mock.return_value = get_fake_private_key

    get_key_mock.return_value = None
    with pytest.raises(ApiException) as ex:
        await decrypt(message)

    assert ex.value.code == 400  # pylint: disable=E1101
    assert ex.value.message == 'Bad Request. Decrypt process failed'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'rsa:decrypt-process-fail'


@pytest.mark.asyncio
@pytest.mark.parametrize('message', [123, True])
@patch('app.utils.rsa_util._get_private_key')
async def test_rsa_decrypt_message_fail_incorrect_message(_get_private_key_mock, message, get_fake_private_key):
    _get_private_key_mock.return_value = get_fake_private_key

    with pytest.raises(ApiException) as ex:
        await decrypt(message)

    assert ex.value.code == 400  # pylint: disable=E1101
    assert ex.value.message == 'Bad Request. Decrypt process failed'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'rsa:decrypt-process-fail'
