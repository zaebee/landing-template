import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BlogPost(_message.Message):
    __slots__ = ("id", "title", "excerpt", "cta")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    EXCERPT_FIELD_NUMBER: _ClassVar[int]
    CTA_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: _common_pb2.I18nString
    excerpt: _common_pb2.I18nString
    cta: _common_pb2.CTA
    def __init__(self, id: _Optional[str] = ..., title: _Optional[_Union[_common_pb2.I18nString, _Mapping]] = ..., excerpt: _Optional[_Union[_common_pb2.I18nString, _Mapping]] = ..., cta: _Optional[_Union[_common_pb2.CTA, _Mapping]] = ...) -> None: ...
