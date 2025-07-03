import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TestimonialItem(_message.Message):
    __slots__ = ("text", "author", "author_image")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_IMAGE_FIELD_NUMBER: _ClassVar[int]
    text: _common_pb2.I18nString
    author: _common_pb2.I18nString
    author_image: _common_pb2.Image
    def __init__(self, text: _Optional[_Union[_common_pb2.I18nString, _Mapping]] = ..., author: _Optional[_Union[_common_pb2.I18nString, _Mapping]] = ..., author_image: _Optional[_Union[_common_pb2.Image, _Mapping]] = ...) -> None: ...
