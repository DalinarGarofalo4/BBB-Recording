from pydantic import BaseModel


class XBearerSchema(BaseModel):
    user: str
    token: str
