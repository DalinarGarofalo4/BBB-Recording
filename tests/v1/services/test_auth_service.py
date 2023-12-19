import pytest

from app.api.services.auth_service import AuthService
from app.exceptions import ApiException


@pytest.mark.asyncio
async def test_verify_access_token_401():
    with pytest.raises(ApiException) as ex:
        await auth_service.verify_access_token(token="fake_token")

    assert ex.value.code == 401  # pylint: disable=E1101
    assert ex.value.message == 'Unauthorized. Authorization error: Not enough segments. Could not validate credentials'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'auth:token-invalid'


auth_service = AuthService()


@pytest.mark.asyncio
async def test_get_current_user_wrong_algorithm(get_token_with_algorithm_wrong):
    with pytest.raises(ApiException) as ex:
        await auth_service.verify_access_token(token=get_token_with_algorithm_wrong)

    assert ex.value.code == 401  # pylint: disable=E1101
    assert ex.value.message == 'Unauthorized. Authorization error: The specified alg value is not allowed. ' \
                               'Could not validate credentials'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'auth:token-invalid'


@pytest.mark.asyncio
@pytest.mark.parametrize('x_bearer, result', [
    ('{"user": "username_1", "token": "fake_token"}', {"user": "username_1", "token": "fake_token"})
])
async def test_parse_x_bearer(x_bearer, result):
    assert result == await auth_service.parse_x_bearer(x_bearer)


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
async def test_parse_x_bearer_400(x_bearer):
    with pytest.raises(ApiException) as ex:
        await auth_service.parse_x_bearer(x_bearer)

    assert ex.value.code == 400  # pylint: disable=E1101
    assert ex.value.message == 'Bad Request. Incorrect X-BEARER.'
    assert ex.value.type == 'ErrorResponse'
    assert ex.value.subtype == 'auth:user-invalid-credentials'
