import pytest

from app.api.v1.metadata import API_ROUTES_PREFIX
from app.config import current
from tests.conftest import TestClient


@pytest.mark.asyncio
async def test_get_version_endpoint_200(client: TestClient, generate_fake_token: str) -> None:
    headers = {'Authorization': f'Bearer {generate_fake_token}'}
    response = client.get(f'{API_ROUTES_PREFIX}/version', headers=headers)
    data = response.json()

    assert data.get('code') == 200
    assert data.get('type') == 'VersionResponse'
    assert str(data.get('data').get('version')) == str(current.VERSION)


@pytest.mark.asyncio
async def test_get_version_endpoint_403(client: TestClient) -> None:
    response = client.get(f'{API_ROUTES_PREFIX}/version')
    data = response.json()

    assert data.get('code') == 403
    assert data.get('type') == 'ErrorResponse'
    assert data.get('message') == 'Forbidden'
    assert data.get('detail') == 'Not authenticated'


@pytest.mark.asyncio
async def test_get_version_endpoint_401(client: TestClient) -> None:
    headers = {'Authorization': 'Bearer fake-token'}
    response = client.get(f'{API_ROUTES_PREFIX}/version', headers=headers)
    data = response.json()

    assert data.get('code') == 401
    assert data.get('type') == 'ErrorResponse'
    assert data.get('subtype') == 'auth:token-invalid'
    assert data.get('message') == 'Unauthorized. Authorization error: Not enough segments. ' \
                                  'Could not validate credentials'
