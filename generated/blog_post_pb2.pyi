from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BlogPost(_message.Message):
    __slots__ = ("id", "title_i18n_key", "excerpt_i18n_key", "cta_i18n_key", "link")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_I18N_KEY_FIELD_NUMBER: _ClassVar[int]
    EXCERPT_I18N_KEY_FIELD_NUMBER: _ClassVar[int]
    CTA_I18N_KEY_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    id: str
    title_i18n_key: str
    excerpt_i18n_key: str
    cta_i18n_key: str
    link: str
    def __init__(self, id: _Optional[str] = ..., title_i18n_key: _Optional[str] = ..., excerpt_i18n_key: _Optional[str] = ..., cta_i18n_key: _Optional[str] = ..., link: _Optional[str] = ...) -> None: ...
