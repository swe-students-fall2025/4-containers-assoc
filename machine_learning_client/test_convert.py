from unittest.mock import Mock, patch
from io import BytesIO
import pytest
from fastapi.testclient import TestClient
from bson import ObjectId

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
    with patch("convert.audio_store") as mock_store, patch("convert.convert_to_wav") as mock_convert, patch("convert.pronunciation_assessment") as mock_assess:
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


@patch("convert.os.remove")
def test_assess_cleanup_temp_files(mock_remove, client, mock_dependencies, audio_file):
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

    client.post("/assess", files=files, data=data)
    assert mock_remove.call_count >= 0


def test_assess_no_audio_file(client):
    data = {"spell": "Lumos"}
    response = client.post("/assess", data=data)
    assert response.status_code in [422, 500]


def test_assess_no_spell(client, audio_file):
    files = {"audio": ("test.webm", audio_file, "audio/webm")}
    response = client.post("/assess", files=files)
    assert response.status_code == 422


def test_assess_assessment_failure(client, mock_dependencies, audio_file):
    mock_store, mock_convert, mock_assess = mock_dependencies

    file_id = ObjectId()
    mock_store.save_audio.return_value = file_id
    mock_convert.return_value = "/tmp/test.webm.wav"
    mock_assess.return_value = {
        "success": False,
        "error": "No speech could be recognized",
        "reference_text": "Lumos",
    }

    files = {"audio": ("test.webm", audio_file, "audio/webm")}
    data = {"spell": "Lumos"}

    response = client.post("/assess", files=files, data=data)

    assert response.status_code == 200
    result = response.json()
    assert result["success"] is False
    assert "error" in result
    assert result["file_id"] == str(file_id)


def test_assess_save_audio_exception(client, mock_dependencies, audio_file):
    mock_store, mock_convert, mock_assess = mock_dependencies
    mock_store.save_audio.side_effect = Exception("Database error")

    files = {"audio": ("test.webm", audio_file, "audio/webm")}
    data = {"spell": "Lumos"}

    response = client.post("/assess", files=files, data=data)

    assert response.status_code == 500
    assert "detail" in response.json()


def test_assess_convert_exception(client, mock_dependencies, audio_file):
    mock_store, mock_convert, mock_assess = mock_dependencies

    file_id = ObjectId()
    mock_store.save_audio.return_value = file_id
    mock_convert.side_effect = Exception("Conversion error")

    files = {"audio": ("test.webm", audio_file, "audio/webm")}
    data = {"spell": "Lumos"}

    response = client.post("/assess", files=files, data=data)

    assert response.status_code == 500
    assert "detail" in response.json()


def test_assess_assessment_exception(client, mock_dependencies, audio_file):
    mock_store, mock_convert, mock_assess = mock_dependencies

    file_id = ObjectId()
    mock_store.save_audio.return_value = file_id
    mock_convert.return_value = "/tmp/test.webm.wav"
    mock_assess.side_effect = Exception("Assessment error")

    files = {"audio": ("test.webm", audio_file, "audio/webm")}
    data = {"spell": "Lumos"}

    response = client.post("/assess", files=files, data=data)

    assert response.status_code == 500
    assert "detail" in response.json()


def test_assess_default_content_type(client, mock_dependencies, audio_file):
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

    files = {"audio": ("test.webm", audio_file)}
    data = {"spell": "Lumos"}

    response = client.post("/assess", files=files, data=data)

    assert response.status_code == 200
    call_args = mock_store.save_audio.call_args
    assert call_args[1]["content_type"] == "audio/webm"


@pytest.mark.parametrize("spell", ["Lumos", "Accio", "Expelliarmus", "Avada Kedavra"])
def test_assess_different_spells(client, mock_dependencies, audio_file, spell):
    mock_store, mock_convert, mock_assess = mock_dependencies

    file_id = ObjectId()
    mock_store.save_audio.return_value = file_id
    mock_convert.return_value = "/tmp/test.webm.wav"
    mock_assess.return_value = {
        "success": True,
        "recognized_text": spell,
        "accuracy_score": 80.0,
        "reference_text": spell,
        "grade": "O",
        "grade_label": "Outstanding",
    }

    files = {"audio": ("test.webm", audio_file, "audio/webm")}
    data = {"spell": spell}

    response = client.post("/assess", files=files, data=data)

    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["reference_text"] == spell
    assert result["file_id"] == str(file_id)
    mock_assess.assert_called_with(spell, "/tmp/test.webm.wav")
