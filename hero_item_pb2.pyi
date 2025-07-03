import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HeroItemContent(_message.Message):
    __slots__ = ("title", "subtitle", "cta", "variation_id")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUBTITLE_FIELD_NUMBER: _ClassVar[int]
    CTA_FIELD_NUMBER: _ClassVar[int]
    VARIATION_ID_FIELD_NUMBER: _ClassVar[int]
    title: _common_pb2.I18nString
    subtitle: _common_pb2.I18nString
    cta: _common_pb2.CTA
    variation_id: str
    def __init__(self, title: _Optional[_Union[_common_pb2.I18nString, _Mapping]] = ..., subtitle: _Optional[_Union[_common_pb2.I18nString, _Mapping]] = ..., cta: _Optional[_Union[_common_pb2.CTA, _Mapping]] = ..., variation_id: _Optional[str] = ...) -> None: ...

class HeroItem(_message.Message):
    __slots__ = ("variations", "default_variation_id")
    VARIATIONS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VARIATION_ID_FIELD_NUMBER: _ClassVar[int]
    variations: _containers.RepeatedCompositeFieldContainer[HeroItemContent]
    default_variation_id: str
    def __init__(self, variations: _Optional[_Iterable[_Union[HeroItemContent, _Mapping]]] = ..., default_variation_id: _Optional[str] = ...) -> None: ...
