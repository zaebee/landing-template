import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PortfolioItem(_message.Message):
    __slots__ = ("id", "image", "details")
    ID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    id: str
    image: _common_pb2.Image
    details: _common_pb2.TitledBlock
    def __init__(self, id: _Optional[str] = ..., image: _Optional[_Union[_common_pb2.Image, _Mapping]] = ..., details: _Optional[_Union[_common_pb2.TitledBlock, _Mapping]] = ...) -> None: ...
