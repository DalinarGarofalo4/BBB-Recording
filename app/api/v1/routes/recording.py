from typing import Annotated, Union

from fastapi import Header

from app.api.schemas.exception_schema import ApiExceptionResponse
from fastapi import APIRouter, Depends
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED
)

from app.api.schemas.recording_schema import (
    RecordingUploadInput,
    RecordingUploadOutput
)
from app.api.services.auth_service import AuthService
from app.api.services.recording_service import RecordingService

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
    response_model=RecordingUploadOutput,
)
async def upload_recording(
    folder_path: str,
    recording_url: str,
    x_bearer: Annotated[Union[str, None], Header()] = None,
    auth_service: AuthService = Depends(AuthService),
    recording_service: RecordingService = Depends(RecordingService),
    _: dict = Depends(AuthService.verify_access_token)
) -> RecordingUploadOutput:
    """
    Upload recording into user drive.
    - Create folders if don't exist.
    - Upload file to user drive.

    ### NOTICE:
    - `x_bearer` must be in the format: `'{user: 'fake-user', token: 'fake-token'}'`
    """
    x_bearer_schema = await auth_service.parse_x_bearer(x_bearer)
    return await recording_service.upload_recording(
        recording_upload_input=RecordingUploadInput(
            x_bearer_schema=x_bearer_schema, folder_path=folder_path, recording_url=recording_url
        )
    )

