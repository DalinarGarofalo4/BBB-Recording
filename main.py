from fastapi import FastAPI
import uvicorn

from app.api.v1.api import api_v1
from app.api.v1.metadata import (
    API_GENERAL_TAGS, API_ROUTES_PREFIX
)

# init app...
app = FastAPI(openapi_tags=[API_GENERAL_TAGS])

# mount the versions
app.mount(API_ROUTES_PREFIX, api_v1)
