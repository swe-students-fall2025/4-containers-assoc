import os
import pytest
from io import BytesIO
from unittest.mock import Mock, patch
from bson import ObjectId
from fastapi.testclient import TestClient

os.environ["SPEECH_KEY"] = "fake_key"
os.environ["SPEECH_REGION"] = "fake_region"

with patch("audio_store.AudioStore.from_env") as mock_from_env:
    mock_store = Mock()
    mock_from_env.return_value = mock_store
    import convert
    convert.audio_store = mock_store


@pytest.fixture
def client():
    return TestClient(convert.app)


@pytest.fixture
def mock_dependencies():
    with patch("convert.audio_store") as mock_store, \
         patch("convert.convert_to_wav") as mock_convert, \
         patch("convert.pronunciation_assessment") as mock_assess:
        yield mock_store, mock_convert, mock_assess


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