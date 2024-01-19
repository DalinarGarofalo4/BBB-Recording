import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from enum import Enum
from http.client import responses
import logging
import os

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR
)

from app.config import current
from app.error_codes import (
    FILE_ALREADY_EXIST, RSA_DECRYPT_PROCESS_FAIL, RSA_ENCRYPT_PROCESS_FAIL
)
from app.exceptions import ApiException, raise_exception

logger = logging.getLogger(__name__)


class KeyTypeEnum(Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'


def generate_keys() -> None:
    """
    Generate private and public keys
    """
    try:
        # Create keys...
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        public_key = private_key.public_key()

        # Serialize public key to .pem file...
        public_key_pem: bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Serialize private key with password to .pem file...
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                current.RSA.PRIVATE_KEY_PASSWORD.encode('utf-8')
            )
        )

        # Get path for keys...
        rsa_dir = os.path.join(current.BASE_DIR, 'app/api/resources/rsa')

        # Create dir if don't exist.
        if not os.path.exists(rsa_dir):
            os.makedirs(rsa_dir)

        # Export public key...
        public_rsa_path = os.path.join(rsa_dir, 'public.pem')
        _export_key(public_key_pem, public_rsa_path, KeyTypeEnum.PUBLIC)

        # Export private key...
        private_rsa_path = os.path.join(rsa_dir, 'private.pem')
        _export_key(private_key_pem, private_rsa_path, KeyTypeEnum.PRIVATE)
    except ApiException as api_ex:
        raise api_ex
    except Exception as ex:
        msg = f'{responses[HTTP_500_INTERNAL_SERVER_ERROR]}. Generate keys fail'
        raise_exception(ApiException(), HTTP_500_INTERNAL_SERVER_ERROR, msg, None, ex)


def _export_key(key_pem: bytes, key_path: str, key_type: KeyTypeEnum):
    """
    Export public and private keys as .pem file into RSA directory
    """
    _verify_keys(key_path, key_type)

    with open(key_path, 'wb') as file:
        file.write(key_pem)


def _verify_keys(key_path: str, key_type: KeyTypeEnum):
    """
    Verify if private or public key already exists.

    ## NOTE:
    If either of the two exists, the process stops.
    """
    if os.path.exists(key_path):
        msg = f'{responses[HTTP_409_CONFLICT]}. The {key_type.value} file already exist.'
        raise_exception(ApiException(), HTTP_409_CONFLICT, msg, FILE_ALREADY_EXIST)


def _get_key(key_type: KeyTypeEnum):
    """
    Return private or public key
    """
    key_path = os.path.join(current.BASE_DIR, f'app/api/resources/rsa/{key_type.value}.pem')

    if key_type == KeyTypeEnum.PUBLIC:
        with open(key_path) as f:
            key = serialization.load_pem_public_key(
                data=f.read().encode(),
                backend=default_backend()
            )
    else:
        with open(key_path, 'rb') as f:
            key = serialization.load_pem_private_key(  # type: ignore
                data=f.read(),
                password=current.RSA.PRIVATE_KEY_PASSWORD.encode('utf-8'),
                backend=default_backend()
            )
    return key


def _get_public_key():
    return _get_key(KeyTypeEnum.PUBLIC)


def _get_private_key():
    return _get_key(KeyTypeEnum.PRIVATE)


async def encrypt(message: str) -> str:
    """
    Encrypt message using RSA algorithm.
    """
    response = ''
    try:
        public_key = _get_public_key()

        encrypted_message = public_key.encrypt(
            plaintext=message.replace("'", '"').encode(),
            padding=OAEP(
                mgf=MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )

        response = base64.urlsafe_b64encode(encrypted_message).decode()
    except ApiException as api_ex:
        raise api_ex
    except Exception as ex:
        msg = f'{responses[HTTP_400_BAD_REQUEST]}. Encrypt process failed'
        raise_exception(ApiException(), HTTP_400_BAD_REQUEST, msg, RSA_ENCRYPT_PROCESS_FAIL, ex)

    return response


async def decrypt(message: str) -> str:
    """
    Decrypt message using RSA algorithm.
    """
    response = ''
    try:
        private_key = _get_private_key()

        encrypted_message: bytes = base64.urlsafe_b64decode(message)
        decrypted_message = private_key.decrypt(
            ciphertext=encrypted_message,
            padding=OAEP(
                mgf=MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )

        response = decrypted_message.decode()
    except ApiException as api_ex:
        raise api_ex
    except Exception as ex:
        msg = f'{responses[HTTP_400_BAD_REQUEST]}. Decrypt process failed'
        raise_exception(ApiException(), HTTP_400_BAD_REQUEST, msg, RSA_DECRYPT_PROCESS_FAIL, ex)

    return response
