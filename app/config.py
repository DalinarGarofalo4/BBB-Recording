import os
import re
from pathlib import Path

from pydantic_settings import BaseSettings

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


class EnvSettings(BaseSettings):
    class Config:
        env_file = '.env'


class AppSettings(EnvSettings):
    ENVIRONMENT_NAME: str = 'localhost'
    NOSWORK_SITE: str = ''

    class Config:
        env_prefix = 'APP_'


class NextCloudSettings(EnvSettings):
    API_URL: str = 'https://nextcloud.local'
    SECURE: bool = True
    WEBDAV_API: str = 'remote.php/dav'
    DOWNLOAD_SERVER: str = ''
    RECORDING_FOLDER: str = 'example/recording'

    class Config:
        env_prefix = 'NEXT_CLOUD_'


class BBBSettings(EnvSettings):
    SERVER: str = 'nextcloud.local'
    METADATA_FILENAME: str = 'bbb-player-metadata.json'
    DOWNLOADED_MEETINGS_FOLDER: str = 'downloadedMeetings'
    DOWNLOADED_FULLY_FILENAME: str = 'rec_fully_downloaded.txt'
    DEFAULT_COMBINED_VIDEO_NAME: str = 'combine-output'
    COMBINED_VIDEO_FORMAT: str = 'mkv'
    INFO_VERSION: str = '1'
    PLAYBACK_VERSION: str = '3.1.1'

    class Config:
        env_prefix = 'BBB_'


class APISettings(EnvSettings):
    HOST: str = 'http://127.0.0.1'
    SECURE: bool = False
    PREFIX: str = API_PREFIX
    ACTIVE_VERSION: str = 'v1'

    class Config:
        env_prefix = 'API_'


class JWTSettings(EnvSettings):
    AUD_NEXTCLOUD: str = 'bbb-recording'
    ISS_NEXTCLOUD: str = 'NosWork'
    DEFAULT_TTL_MINUTES: int = 60 * 24 * 30  # ~ 1 month
    SECRET_KEY: str = ''
    ALGORITHM: str = 'HS256'

    class Config:
        env_prefix = 'JWT_'


class RSASettings(EnvSettings):
    PRIVATE_KEY_PASSWORD: str = ''

    class Config:
        env_prefix = 'RSA_'


class EmailSettings(EnvSettings):
    SMTP_SERVER: str = ''
    SMTP_PORT: int = 587
    SENDER_EMAIL: str = ''
    SENDER_PASSWORD: str = ''

    class Config:
        env_prefix = 'EMAIL_'


class BaseConfig:
    LOG_LEVEL: str = 'info'
    DEBUG: bool = False

    PROJECT_NAME: str = 'BBB Recording'
    VERSION: str = _get_version()
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    SWAGGER_URL: str = f'{SWAGGER_DOC_PATH}'
    OPENAPI_URL: str = f'{OPENAPI_DOC_URL}'
    SWAGGER_PUBLIC_URL: str = f'/public{SWAGGER_DOC_PATH}'
    OPENAPI_PUBLIC_URL: str = f'/public{OPENAPI_DOC_URL}'

    NEXT_CLOUD: NextCloudSettings = NextCloudSettings()
    BBB: BBBSettings = BBBSettings()
    API: APISettings = APISettings()

    JWT: JWTSettings = JWTSettings()

    RSA: RSASettings = RSASettings()

    EMAIL: EmailSettings = EmailSettings()

    APP: AppSettings = AppSettings()


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
current: BaseConfig = config[os.environ.get('APP_ENVIRONMENT_NAME', 'development').lower()]()
