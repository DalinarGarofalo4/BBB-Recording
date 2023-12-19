import os
import re
from pathlib import Path

from pydantic import BaseSettings

from app.constants import API_PREFIX, SWAGGER_DOC_PATH, OPENAPI_DOC_URL


def _get_version() -> str:
    with open('./VERSION', 'r') as f:
        version = f.read().strip()

    with Path('./BUILD_METADATA') as f:  # type: ignore
        if f.exists() and f.is_file():  # type: ignore
            build_metadata = f.read_text().strip()  # type: ignore
        else:
            build_metadata = os.getenv('BUILD_METADATA', '')
    if build_metadata:
        build_metadata = re.sub(r'[^0-9A-Za-z-]', '-', build_metadata)
        version = f'{version}+{build_metadata}'
    return version


class NextCloudSettings(BaseSettings):
    API_URL: str = 'https://nextcloud.local'
    SECURE: bool = True
    WEBDAV_API: str = 'remote.php/dav'

    class Config:
        env_prefix = 'NEXT_CLOUD_'


class BBBSettings(BaseSettings):
    SERVER: str = 'https://nextcloud.local'

    class Config:
        env_prefix = 'BBB_'


class APISettings(BaseSettings):
    HOST: str = 'http://127.0.0.1'
    PORT: int = 8000
    SECURE: bool = False

    class Config:
        env_prefix = 'API_'


class JWTSettings(BaseSettings):
    AUD_NEXTCLOUD: str = 'bbb-recording'
    ISS_NEXTCLOUD: str = 'NosWork'
    DEFAULT_TTL_MINUTES: int = 60 * 24 * 30  # ~ 1 month
    SECRET_KEY: str = ''
    ALGORITHM: str = 'HS256'

    class Config:
        env_prefix = 'JWT_'


class EmailSettings(BaseSettings):
    SMTP_SERVER: str = ''
    SMTP_PORT: str = ''
    SENDER_EMAIL: str = ''
    SENDER_PASSWORD: str = ''

    class Config:
        env_prefix = 'EMAIL_'


class BaseConfig:
    ENVIRONMENT_NAME: str = 'localhost'
    LOG_LEVEL: str = 'info'
    DEBUG: bool = False

    PROJECT_NAME: str = 'BBB Recording'
    VERSION: str = _get_version()

    DOWNLOAD_SERVER: str = ''

    API_PREFIX: str = API_PREFIX
    SWAGGER_URL: str = f'{SWAGGER_DOC_PATH}'
    OPENAPI_URL: str = f'{OPENAPI_DOC_URL}'
    SWAGGER_PUBLIC_URL: str = f'/public{SWAGGER_DOC_PATH}'
    OPENAPI_PUBLIC_URL: str = f'/public{OPENAPI_DOC_URL}'

    NEXT_CLOUD: NextCloudSettings = NextCloudSettings()
    BBB: BBBSettings = BBBSettings()
    API: APISettings = APISettings()

    JWT: JWTSettings = JWTSettings()

    EMAIL: EmailSettings = EmailSettings()


class DevelopmentConfig(BaseConfig):
    """Configurations for Development."""
    LOG_LEVEL = 'debug'


class ProductionConfig(BaseConfig):
    """Configurations for Production."""
    LOG_LEVEL: str = 'info'


config = dict(
    development=DevelopmentConfig,
    production=ProductionConfig,
)
current: BaseConfig = config[os.environ.get('ENVIRONMENT_NAME', 'development').lower()]()
