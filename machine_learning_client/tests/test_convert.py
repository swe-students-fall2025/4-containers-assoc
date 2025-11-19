import os
import pytest
from io import BytesIO
from unittest.mock import Mock, patch
from bson import ObjectId
from fastapi.testclient import TestClient
from .. import convert

os.environ["SPEECH_KEY"] = "fake_key"
os.environ["SPEECH_REGION"] = "fake_region"

@pytest.fixture(autouse=True)
def _fake_env(monkeypatch):
    monkeypatch.setenv("SPEECH_KEY", "fake_key")
    monkeypatch.setenv("SPEECH_REGION", "fake_region")
    # If your AudioStore.from_env() uses these:
    # monkeypatch.setenv("MONGO_URI", "mongodb://fake")
    # monkeypatch.setenv("DB_NAME", "testdb")


@pytest.fixture
def client():
    return TestClient(convert.app)


@pytest.fixture
def mock_dependencies(monkeypatch):
    mock_store = Mock()
    mock_convert = Mock()
    mock_assess = Mock()

    # Override attributes on the imported convert module
    monkeypatch.setattr(convert, "audio_store", mock_store)
    monkeypatch.setattr(convert, "convert_to_wav", mock_convert)
    monkeypatch.setattr(convert, "pronunciation_assessment", mock_assess)

    return mock_store, mock_convert, mock_assess


@pytest.fixture
def audio_file():
    return BytesIO(b"fake audio data")


def test_assess_success(client, mock_dependencies, audio_file):
    mock_store, mock_convert, mock_assess = mock_dependencies

    file_id = ObjectId()
    mock_store.save_audio.return_value = file_id
    mock_convert.return_value = "/tmp/test.webm.wav"
    mock_assess.return_value = {
        "success": True,
        "recognized_text": "Lumos",
        "accuracy_score": 85.5,
        "reference_text": "Lumos",
        "grade": "O",
        "grade_label": "Outstanding",
    }

    files = {"audio": ("test.webm", audio_file, "audio/webm")}
    data = {"spell": "Lumos"}

    response = client.post("/assess", files=files, data=data)

    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["recognized_text"] == "Lumos"
    assert result["grade"] == "O"
    assert result["file_id"] == str(file_id)