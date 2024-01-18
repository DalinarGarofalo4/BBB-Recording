import pytest
from unittest.mock import patch

from fastapi.security import HTTPAuthorizationCredentials

from app.api.services.auth_service import AuthService
from app.exceptions import ApiException
from app.utils.rsa_util import encrypt


@pytest.mark.asyncio
async def test_verify_access_token_401():
    with pytest.raises(ApiException) as ex:
        authorization = HTTPAuthorizationCredentials(scheme='Bearer', credentials='fake_token')
        await auth_service.verify_access_token(authorization)

    assert ex.value.code == 401  # pylint: disable=E1101
    assert ex.value.message == 'Unauthorized. Authorization error: Not enough segments. Could not validate credentials'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'auth:token-invalid'


auth_service = AuthService()


@pytest.mark.asyncio
async def test_get_current_user_wrong_algorithm(get_token_with_algorithm_wrong):
    with pytest.raises(ApiException) as ex:
        authorization = HTTPAuthorizationCredentials(scheme='Bearer', credentials=get_token_with_algorithm_wrong)
        await auth_service.verify_access_token(authorization)

    assert ex.value.code == 401  # pylint: disable=E1101
    assert ex.value.message == 'Unauthorized. Authorization error: The specified alg value is not allowed. ' \
                               'Could not validate credentials'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'auth:token-invalid'


@pytest.mark.asyncio
@pytest.mark.parametrize('x_bearer, user, token', [
    ('{"user": "username_1", "token": "fake_token"}', 'username_1', 'fake_token'),
    ('{"user": "user_example", "token": "vLUif4Bbvqz3s8H9RypzzSNb56U"}', 'user_example', 'vLUif4Bbvqz3s8H9RypzzSNb56U')
])
@patch('app.utils.rsa_util._get_public_key')
@patch('app.utils.rsa_util._get_private_key')
async def test_parse_x_bearer(
    _get_private_key_mock, _get_public_key_mock,
    x_bearer, user, token, get_fake_public_key, get_fake_private_key
):
    _get_private_key_mock.return_value = get_fake_private_key
    _get_public_key_mock.return_value = get_fake_public_key

    x_bearer_schema = await auth_service.parse_x_bearer(x_bearer=await encrypt(x_bearer))
    assert x_bearer_schema.user == user
    assert x_bearer_schema.token == token


@pytest.mark.asyncio
@pytest.mark.parametrize('x_bearer', [
    '{"user": None, "token": None}',
    '{"user": None, "token": "fake_token"}',
    '{"user": "fake_user", "token": None}',
    '{"user": "fake_user"}',
    '{"token": "fake_token"}',
    '{"user": "", "token": ""}',
    '{"user": ""}',
    '{"token": ""}',
])
@patch('app.utils.rsa_util._get_public_key')
@patch('app.utils.rsa_util._get_private_key')
async def test_parse_x_bearer_400(
    _get_private_key_mock, _get_public_key_mock, x_bearer, get_fake_public_key, get_fake_private_key
):
    _get_private_key_mock.return_value = get_fake_private_key
    _get_public_key_mock.return_value = get_fake_public_key

    with pytest.raises(ApiException) as ex:
        await auth_service.parse_x_bearer(x_bearer=await encrypt(x_bearer))

    assert ex.value.code == 400  # pylint: disable=E1101
    assert ex.value.message == 'Bad Request. Incorrect X-BEARER.'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'auth:user-invalid-credentials'
