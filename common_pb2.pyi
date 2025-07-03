from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class I18nString(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class Image(_message.Message):
    __slots__ = ("src", "alt_text")
    SRC_FIELD_NUMBER: _ClassVar[int]
    ALT_TEXT_FIELD_NUMBER: _ClassVar[int]
    src: str
    alt_text: I18nString
    def __init__(self, src: _Optional[str] = ..., alt_text: _Optional[_Union[I18nString, _Mapping]] = ...) -> None: ...

class CTA(_message.Message):
    __slots__ = ("text", "uri")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    URI_FIELD_NUMBER: _ClassVar[int]
    text: I18nString
    uri: str
    def __init__(self, text: _Optional[_Union[I18nString, _Mapping]] = ..., uri: _Optional[str] = ...) -> None: ...

class TitledBlock(_message.Message):
    __slots__ = ("title", "description")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    title: I18nString
    description: I18nString
    def __init__(self, title: _Optional[_Union[I18nString, _Mapping]] = ..., description: _Optional[_Union[I18nString, _Mapping]] = ...) -> None: ...
