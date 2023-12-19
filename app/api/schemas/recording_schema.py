from pydantic import BaseModel

from app.api.schemas.auth_schema import XBearerSchema
from app.api.schemas.base_schema import ResponseBase


class RecordingUploadInput(BaseModel):
    x_bearer_schema: XBearerSchema
    folder_path: str
    recording_url: str


class RecordingUploadOutput(ResponseBase):
    pass
