SWAGGER_DOC_PATH = '/doc/swagger/ui/'
OPENAPI_DOC_URL = '/swagger.json'
API_PREFIX = '/recording/api'

ADMIN_SCOPE = 'admin'

jwt_description = """
All authenticated endpoints require a valid API token passed
in the `Authorization` HTTP header.

This token will be provided to you.

The HTTP `Authorization` header should be populated for each request with the Bearer prefix:

```
Authorization: Bearer <YOUR_TOKEN>
```

<div class="warning">

### Security Reminder
</div>

The API will respond to requests without the correct authentication in two different ways:

* A `401 Unauthorized` HTTP status code will be returned if:
    * the token is expired
    * the token signature is invalid (truncated, or the token has been tampered)
    * the token doesn’t contain the correct claims
* A `403 Forbidden` HTTP status code will be returned if:
    * the token is missing, is not prefixed with `Bearer`

**You should never share your complete token! You should always remove the signature.**

You can learn more about JWT, how they work, the best practices on https://jwt.io/.

"""
