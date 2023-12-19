from app.config import current

SWAGGER_DOC_PATH = current.SWAGGER_URL
API_HOST = current.API.HOST
API_PORT = current.API.PORT
VERSION = current.VERSION

API_ROUTES_PREFIX = f'{current.API_PREFIX}/v1'


DESCRIPTION = f"""
Recording API v{VERSION}

The Recording API allows managing recordings made by the user in Big Blue Button through NextCloud.

A Swagger/OpenSpec UI is also available and let you directly interact with this data.

You can access the interactive UI <a href="{API_HOST}:{API_PORT}{API_ROUTES_PREFIX}{SWAGGER_DOC_PATH}">here</a>.

"""

API_GENERAL_TAGS = {
    'name': 'v1',
    'description': 'You can access the interactive UI here:',
    'externalDocs': {
        'description': f"""{API_HOST}:{API_PORT}{API_ROUTES_PREFIX}{SWAGGER_DOC_PATH}""",
        'url': f"""{API_HOST}:{API_PORT}{API_ROUTES_PREFIX}{SWAGGER_DOC_PATH}"""
    }
}