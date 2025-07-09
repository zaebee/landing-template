from google.protobuf import json_format as pb_json_format


def test_protobuf_import():
    assert pb_json_format is not None
