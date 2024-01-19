from pydantic import BaseModel

from app.api.schemas.auth_schema import XBearerSchema
from app.api.schemas.base_schema import ResponseBase
from app.config import current


class RecordingUploadInput(BaseModel):
    x_bearer_schema: XBearerSchema
    recording_url: str


class EmailInput(BaseModel):
    to_email: str
    room_name: str
    download_meeting_dir: str
    download_link: str
    upload_link: str
    sender_email: str = current.EMAIL.SENDER_EMAIL
    smtp_server: str = current.EMAIL.SMTP_SERVER
    smtp_port: int = current.EMAIL.SMTP_PORT


class RecordingSendEmailInput(BaseModel):
    x_bearer_encrypted: str
    url: str
    meeting_name: str
    email: str


class RecordingUploadResponse(ResponseBase):
    pass


class RecordingSendEmailResponse(ResponseBase):
    pass
