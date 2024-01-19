import json

from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)

from app.api.schemas.exception_schema import ApiExceptionResponse
from app.api.services.auth_service import AuthService
from app.api.schemas.utils_schema import (
    EncryptMessageSchema, EncryptMessageResponse, DecryptMessageSchema, DecryptMessageResponse, MessageInputSchema,
    VersionSchema, VersionResponse
)
from app.config import current
from app.utils.rsa_util import encrypt, decrypt

router = APIRouter(
    responses={
        HTTP_401_UNAUTHORIZED: {
            'model': ApiExceptionResponse,
        },
        HTTP_403_FORBIDDEN: {
            'model': ApiExceptionResponse
        }
    }
)


@router.get(
    '/version',
    summary='Return version directly',
    response_model=VersionResponse
)
async def get_version(_: dict = Depends(AuthService.verify_access_token)):
    return VersionResponse(data=VersionSchema(version=current.VERSION))


@router.post(
    '/encrypt_message',
    summary='Encrypt test message',
    response_model=EncryptMessageResponse
)
async def encrypt_message(
        message_input: MessageInputSchema, _: dict = Depends(AuthService.verify_access_token)
) -> EncryptMessageResponse:
    encrypted_message = await encrypt(message_input.message)
    return EncryptMessageResponse(data=EncryptMessageSchema(encrypted_message=encrypted_message))


@router.post(
    '/decrypt_message',
    summary='Decrypt test message',
    response_model=DecryptMessageResponse
)
async def decrypt_message(
        message_input: MessageInputSchema, _: dict = Depends(AuthService.verify_access_token)
) -> DecryptMessageResponse:
    decrypted_message = await decrypt(message_input.message)
    return DecryptMessageResponse(data=DecryptMessageSchema(decrypted_message=json.loads(decrypted_message)))
