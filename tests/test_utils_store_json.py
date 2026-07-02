import base64
import json

from web2vec.utils import store_json


def test_store_json_serializes_ascii_bytes(tmp_path):
    """Ensure bytes containing UTF-8 data are persisted as text."""
    payload = b"hello world"
    output = tmp_path / "ascii.json"

    store_json({"payload": payload}, str(output))

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["payload"] == payload.decode("utf-8")


def test_store_json_serializes_binary_bytes(tmp_path):
    """Ensure non-text bytes are base64-encoded for JSON output."""
    payload = b"\xff\xfe\xfd"
    output = tmp_path / "binary.json"

    store_json({"payload": payload}, str(output))

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["payload"] == base64.b64encode(payload).decode("ascii")
