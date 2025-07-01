from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PortfolioItem(_message.Message):
    __slots__ = ("id", "img_src", "img_alt", "title_i18n_key", "desc_i18n_key")
    ID_FIELD_NUMBER: _ClassVar[int]
    IMG_SRC_FIELD_NUMBER: _ClassVar[int]
    IMG_ALT_FIELD_NUMBER: _ClassVar[int]
    TITLE_I18N_KEY_FIELD_NUMBER: _ClassVar[int]
    DESC_I18N_KEY_FIELD_NUMBER: _ClassVar[int]
    id: str
    img_src: str
    img_alt: str
    title_i18n_key: str
    desc_i18n_key: str
    def __init__(self, id: _Optional[str] = ..., img_src: _Optional[str] = ..., img_alt: _Optional[str] = ..., title_i18n_key: _Optional[str] = ..., desc_i18n_key: _Optional[str] = ...) -> None: ...
