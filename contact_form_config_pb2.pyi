from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ContactFormConfig(_message.Message):
    __slots__ = ("form_action_uri", "success_message_key", "error_message_key")
    FORM_ACTION_URI_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_MESSAGE_KEY_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_KEY_FIELD_NUMBER: _ClassVar[int]
    form_action_uri: str
    success_message_key: str
    error_message_key: str
    def __init__(self, form_action_uri: _Optional[str] = ..., success_message_key: _Optional[str] = ..., error_message_key: _Optional[str] = ...) -> None: ...
