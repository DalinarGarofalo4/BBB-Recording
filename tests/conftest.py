from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from jose import jwt
from typing import Any, Dict, Generator, Optional
import os

from fastapi.testclient import TestClient
import pytest
from faker import Faker

from app.config import current
from main import app


faker = Faker()
ShadowState = Dict[str, Any]
ShadowReported = Dict[str, Any]


@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as test_client:
        yield test_client


def generate_bearer_token(claims: dict, secret: Optional[str] = None, algorithm: Optional[str] = None):
    return jwt.encode(
        claims,
        key=current.JWT.SECRET_KEY if secret is None else secret,
        algorithm=current.JWT.ALGORITHM if algorithm is None else algorithm
    )


@pytest.fixture()
def generate_fake_token() -> str:
    return generate_bearer_token({})


@pytest.fixture()
def get_token_with_algorithm_wrong():
    """
    Get fake bearer token.
    - Algorithm used: HS384
    """
    return generate_bearer_token({}, None, 'HS384')


@pytest.fixture()
def get_fake_public_key():
    key_path = os.path.join(current.BASE_DIR, 'tests/v1/resources/rsa_fake/public.pem')
    with open(key_path) as f:
        return serialization.load_pem_public_key(
            data=f.read().encode(),
            backend=default_backend()
        )


@pytest.fixture()
def get_fake_private_key():
    key_path = os.path.join(current.BASE_DIR, 'tests/v1/resources/rsa_fake/private.pem')
    with open(key_path) as f:
        return serialization.load_pem_private_key(  # type: ignore
            data=f.read().encode('utf-8'),
            password=current.RSA.PRIVATE_KEY_PASSWORD.encode('utf-8'),
            backend=default_backend()
        )
