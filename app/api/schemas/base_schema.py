from typing import TypeVar, Generic, Optional

from pydantic import BaseModel

DataType = TypeVar('DataType')
T = TypeVar('T')


class ResponseBase(BaseModel, Generic[T]):
    code: int = 200
    type: str = 'ResponseType'

    def __init__(cls, response_type: str = '', **kwargs):  # pylint: disable=no-self-argument
        super().__init__(**kwargs)
        cls.type = response_type or cls.__class__.__name__


class GetResponseBase(ResponseBase[DataType], Generic[DataType]):
    """
    Generic Get Response
    """
    data: Optional[DataType]
