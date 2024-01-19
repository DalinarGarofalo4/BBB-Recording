from fastapi import APIRouter, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_400_BAD_REQUEST

from app.api.v1.metadata import DESCRIPTION
from app.api.v1.routes import recording, utils
from app.config import current
from app.exceptions import set_exception_handlers

api_router = APIRouter()
api_router.include_router(recording.router, tags=['Recording'])
api_router.include_router(utils.router, tags=['Utils'])

# init API v1
api_v1 = FastAPI(
    title=current.PROJECT_NAME,
    version=current.VERSION,
    openapi_url=current.OPENAPI_URL,
    docs_url=current.SWAGGER_URL,
    description=DESCRIPTION
)

# Load routers...
api_v1.include_router(api_router)

# Add custom exception Handlers
exc_for_default_handler = {
    RequestValidationError: HTTP_400_BAD_REQUEST
}
set_exception_handlers(
    api_v1, jsonable_encoder, exc_for_default_handler=exc_for_default_handler  # type: ignore[arg-type]
)
