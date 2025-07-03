import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NavItem(_message.Message):
    __slots__ = ("label", "href", "animation_hint")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    HREF_FIELD_NUMBER: _ClassVar[int]
    ANIMATION_HINT_FIELD_NUMBER: _ClassVar[int]
    label: _common_pb2.I18nString
    href: str
    animation_hint: str
    def __init__(self, label: _Optional[_Union[_common_pb2.I18nString, _Mapping]] = ..., href: _Optional[str] = ..., animation_hint: _Optional[str] = ...) -> None: ...

class Navigation(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[NavItem]
    def __init__(self, items: _Optional[_Iterable[_Union[NavItem, _Mapping]]] = ...) -> None: ...
