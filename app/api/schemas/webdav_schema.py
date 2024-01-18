from pydantic import BaseModel
from typing import Any, Optional


class WebDAVRequestInput(BaseModel):
    method: str
    url: str
    headers: Optional[dict] = None
    body: Optional[Any] = None


class WebDAVCreateFolderDTO(BaseModel):
    folder_name: str


class WebDAVGetFileDTO(BaseModel):
    file_url: str


class WebDAVUploadFileDTO(BaseModel):
    file_name: str
    file: bytes
    full_folder_path: str
