from fastapi import Depends

from app.api.schemas.recording_schema import (
    RecordingUploadInput,
    RecordingUploadOutput
)
from app.api.schemas.webdav_schema import (
    WebDAVCreateFolderDTO,
    WebDAVGetFileDTO,
    WebDAVUploadFileDTO
)
from app.api.services.web_dav_service import WebDAVService
from app.utils.recording_util import get_full_folder_path


class RecordingService:

    def __init__(self, webdav_service: WebDAVService = Depends(WebDAVService)):
        self._webdav_service = webdav_service

    async def upload_recording(self, recording_upload_input: RecordingUploadInput) -> RecordingUploadOutput:
        """
        Upload file to the user's drive in NextCloud...
        """
        x_bearer_schema = recording_upload_input.x_bearer_schema
        folder_path = recording_upload_input.folder_path
        recording_url = recording_upload_input.recording_url

        # configure webdav client...
        await self._webdav_service.configure_webdav_client(x_bearer_schema)

        # create folders...
        full_folder_path = await self.create_full_folder_path(folder_path)

        # get file...
        file_name, file = await self._webdav_service.get_file(get_file_dto=WebDAVGetFileDTO(file_url=recording_url))

        # upload file...
        status = await self._webdav_service.upload_file(
            upload_file_dto=WebDAVUploadFileDTO(file_name=file_name, file=file, full_folder_path=full_folder_path)
        )

        return RecordingUploadOutput(code=status)

    async def create_full_folder_path(self, folder_path: str) -> str:
        """
        Create full path from some folder paths in user drive and return it...
        """
        full_folder_path = await get_full_folder_path(folder_path)
        for folder_name in full_folder_path:
            # create if don't exist...
            await self._webdav_service.create_folder(create_folder_dto=WebDAVCreateFolderDTO(folder_name=folder_name))
        return '' if not len(full_folder_path) else full_folder_path[-1]
