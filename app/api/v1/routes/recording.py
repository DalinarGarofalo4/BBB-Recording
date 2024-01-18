from typing import Annotated, Union
import logging

from fastapi import Header
from fastapi.responses import RedirectResponse

from app.api.schemas.exception_schema import ApiExceptionResponse
from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_200_OK,
    HTTP_302_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED
)

from app.api.schemas.recording_schema import (
    RecordingSendEmailInput,
    RecordingUploadInput,
    RecordingSendEmailResponse
)
from app.api.services.auth_service import AuthService
from app.api.services.recording_service import RecordingService
from app.config import current

logger = logging.getLogger(__name__)

router = APIRouter(
    responses={
        HTTP_400_BAD_REQUEST: {
            'model': ApiExceptionResponse,
        },
        HTTP_401_UNAUTHORIZED: {
            'model': ApiExceptionResponse,
        },
        HTTP_403_FORBIDDEN: {
            'model': ApiExceptionResponse
        },
        HTTP_404_NOT_FOUND: {
            'model': ApiExceptionResponse
        },
        HTTP_405_METHOD_NOT_ALLOWED: {
            'model': ApiExceptionResponse
        }
    }
)


@router.get(
    '/upload/recording',
    summary='Upload recording into user drive',
    status_code=HTTP_302_FOUND
)
async def upload_recording(
    recording_url: str,
    x_header: str,
    auth_service: AuthService = Depends(AuthService),
    recording_service: RecordingService = Depends(RecordingService)
) -> RedirectResponse:
    """
    Upload recording into user drive.
    - Create folders if don't exist.
    - Upload file to user drive.
    """
    x_bearer_schema = await auth_service.parse_x_bearer(x_header)

    await recording_service.upload_recording(
        recording_upload_input=RecordingUploadInput(x_bearer_schema=x_bearer_schema, recording_url=recording_url)
    )
    return RedirectResponse(f'{current.NEXT_CLOUD.API_URL}/apps/files', status_code=HTTP_302_FOUND)


@router.get(
    '/video/{url:path}:{meeting_name}/{email}',
    summary='Send email with link for download and upload into user drive',
    status_code=HTTP_200_OK,
    response_model=RecordingSendEmailResponse
)
async def send_email_with_recording_links(
    url: str, meeting_name: str, email: str,
    x_bearer: Annotated[str, Header()],
    recording_service: RecordingService = Depends(RecordingService),
    _: dict = Depends(AuthService.verify_access_token)
) -> RecordingSendEmailResponse:
    """
    Send email with links for download recording and the option of loading it to user drive.

    ### NOTICE:
    - `x_bearer` must be in the format: `'{user: 'fake-user', token: 'fake-token'}'`
    """
    await recording_service.send_email(
        recording_send_email_input=RecordingSendEmailInput(
            x_bearer_encrypted=x_bearer, url=url, meeting_name=meeting_name, email=email
        )
    )

    return RecordingSendEmailResponse()
