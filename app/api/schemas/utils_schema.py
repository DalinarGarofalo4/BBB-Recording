from pydantic import BaseModel

from app.api.schemas.base_schema import GetResponseBase


class VersionSchema(BaseModel):
    version: str


class VersionResponse(GetResponseBase[VersionSchema]):
    pass


class MessageInputSchema(BaseModel):
    message: str


class EncryptMessageSchema(BaseModel):
    encrypted_message: str


class DecryptMessageSchema(BaseModel):
    decrypted_message: dict


class EncryptMessageResponse(GetResponseBase[EncryptMessageSchema]):
    pass


class DecryptMessageResponse(GetResponseBase[DecryptMessageSchema]):
    pass
