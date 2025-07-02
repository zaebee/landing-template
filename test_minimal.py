import pytest
from google.protobuf import json_format

def test_protobuf_import():
    assert json_format is not None
