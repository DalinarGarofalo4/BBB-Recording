import base64
import os
import shutil

from fastapi import Depends

from app.api.schemas.recording_schema import (
    EmailInput,
    RecordingSendEmailInput,
    RecordingUploadInput,
    RecordingUploadResponse
)
from app.api.schemas.webdav_schema import (
    WebDAVCreateFolderDTO,
    WebDAVGetFileDTO,
    WebDAVUploadFileDTO
)
from app.api.services.web_dav_service import WebDAVService
from app.config import current
from app.exceptions import ApiException
from app.utils.recording_util import get_full_folder_path, send_email
from app.utils.file_util import combine, download_script


class RecordingService:

    def __init__(self, webdav_service: WebDAVService = Depends(WebDAVService)):
        self._webdav_service = webdav_service

    async def upload_recording(self, recording_upload_input: RecordingUploadInput) -> RecordingUploadResponse:
        """
        Upload file to the user's drive in NextCloud...
        """
        x_bearer_schema = recording_upload_input.x_bearer_schema
        recording_url = recording_upload_input.recording_url
        folder_path = current.NEXT_CLOUD.RECORDING_FOLDER

        # configure webdav client...
        await self._webdav_service.configure_webdav_client(x_bearer_schema)

        # create folders...
        full_folder_path = await self._create_full_folder_path(folder_path)

        # get file...
        file_name, file = await self._webdav_service.get_file(get_file_dto=WebDAVGetFileDTO(file_url=recording_url))

        # upload file...
        status = await self._webdav_service.upload_file(
            upload_file_dto=WebDAVUploadFileDTO(file_name=file_name, file=file, full_folder_path=full_folder_path)
        )

        return RecordingUploadResponse(code=status)

    async def _create_full_folder_path(self, folder_path: str) -> str:
        """
        Create full path from some folder paths in user drive and return it...
        """
        full_folder_path = await get_full_folder_path(folder_path)
        for folder_name in full_folder_path:
            # create if don't exist...
            await self._webdav_service.create_folder(create_folder_dto=WebDAVCreateFolderDTO(folder_name=folder_name))
        return '' if not len(full_folder_path) else full_folder_path[-1]

    # TODO: missing unit tests...
    @staticmethod
    async def send_email(recording_send_email_input: RecordingSendEmailInput) -> None:
        x_bearer_encrypted = recording_send_email_input.x_bearer_encrypted
        url = recording_send_email_input.url
        meeting_name = recording_send_email_input.meeting_name
        user_email = recording_send_email_input.email

        combine_boolean, folder_name, folder_exists = await download_script(url, meeting_name)

        # Check if the folder for the downloaded meeting exists
        if not folder_exists:
            try:
                await combine(folder_name, combine_boolean)
            except ApiException:
                # If an exception occurs, remove the downloaded meeting folder and try combining again
                shutil.rmtree(os.path.join(
                    current.BASE_DIR, current.BBB.DOWNLOADED_MEETINGS_FOLDER, meeting_name + "-" + url[-5:]
                ))
                await combine(folder_name, combine_boolean)

        download_meeting_dir = f'{meeting_name}-{url[-5:]}'
        download_link = f'{current.NEXT_CLOUD.DOWNLOAD_SERVER}/{download_meeting_dir}/{download_meeting_dir}.zip'

        host = current.API.HOST
        api_prefix = current.API.PREFIX
        active_version = current.API.ACTIVE_VERSION
        endpoint = 'upload/recording'
        recording_url = f'{current.NEXT_CLOUD.DOWNLOAD_SERVER}/{download_meeting_dir}/{download_meeting_dir}.mp4'

        # set base64 to urlsafe...
        x_bearer_encrypted = base64.urlsafe_b64encode(base64.urlsafe_b64decode(x_bearer_encrypted)).decode()

        upload_link = f'{host}{api_prefix}/{active_version}/{endpoint}?' \
                      f'recording_url={recording_url}&x_header={x_bearer_encrypted}'

        send_email(
            EmailInput(
                to_email=user_email, room_name=meeting_name, download_meeting_dir=download_meeting_dir,
                download_link=download_link, upload_link=upload_link
            )
        )
