import os
import re
from pathlib import Path

from app.config import current


def test_get_version():
    with open('./VERSION', 'r') as f_version:
        version = f_version.read().strip()
    assert version is not None

    with Path('./BUILD_METADATA') as f_metadata:  # type: ignore
        if f_metadata.exists() and f_metadata.is_file():  # type: ignore
            build_metadata = f_metadata.read_text().strip()  # type: ignore
            assert build_metadata is not None
        else:
            build_metadata = os.getenv('BUILD_METADATA', '')
            assert build_metadata is not None

    if build_metadata:
        build_metadata = re.sub(r'[^0-9A-Za-z-]', '-', build_metadata)
        assert build_metadata is not None
        version = f'{version}+{build_metadata}'

    assert version == current.VERSION


def test_current_config():
    assert current.API.HOST == os.getenv('API_HOST')
    assert current.API.PORT == int(os.getenv('API_PORT'))
    assert current.API.SECURE == (os.getenv('API_SECURE').lower() == 'true')

    assert current.NEXT_CLOUD.API_URL == os.getenv('NEXT_CLOUD_API_URL')
    assert current.NEXT_CLOUD.WEBDAV_API == os.getenv('NEXT_CLOUD_WEBDAV_API')

    assert current.BBB.SERVER == os.getenv('BBB_SERVER')

    assert current.JWT.SECRET_KEY == os.getenv('JWT_SECRET_KEY')
    assert current.JWT.ALGORITHM == os.getenv('JWT_ALGORITHM')

    assert current.EMAIL.SMTP_SERVER == os.getenv('EMAIL_SMTP_SERVER')
    assert current.EMAIL.SMTP_PORT == os.getenv('EMAIL_SMTP_PORT')
    assert current.EMAIL.SENDER_EMAIL == os.getenv('EMAIL_SENDER_EMAIL')
    assert current.EMAIL.SENDER_PASSWORD == os.getenv('EMAIL_SENDER_PASSWORD')
