import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO
from bson import ObjectId
from audio_store import AudioStore


@pytest.fixture
def mock_mongo():
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_attempts_col = MagicMock()
    mock_db.__getitem__.return_value = mock_attempts_col

    mock_gridfs_instance = MagicMock()

    with patch("audio_store.MongoClient", return_value=mock_client) as mock_client_class, \
         patch("audio_store.GridFS", return_value=mock_gridfs_instance) as mock_gridfs_class:
        yield mock_client, mock_db, mock_gridfs_instance, mock_attempts_col

def test_save_audio_basic(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs
    store._attempts_col = mock_attempts_col
    file_id = ObjectId()
    mock_gridfs.put.return_value = file_id

    file_obj = BytesIO(b"fake audio data")
    result_id = store.save_audio(file_obj, spell="Lumos", filename="test.wav", content_type="audio/wav")

    assert result_id == file_id
    mock_gridfs.put.assert_called_once()
    call_args = mock_gridfs.put.call_args
    assert call_args[1]["metadata"]["spell"] == "Lumos"
    mock_attempts_col.insert_one.assert_called_once()


def test_save_audio_with_score(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs
    store._attempts_col = mock_attempts_col
    file_id = ObjectId()
    mock_gridfs.put.return_value = file_id

    file_obj = BytesIO(b"fake audio data")
    store.save_audio(file_obj, spell="Lumos", filename="test.wav", score=85.5)
    call_args = mock_gridfs.put.call_args
    assert call_args[1]["metadata"]["score"] == 85.5
    attempt_call = mock_attempts_col.insert_one.call_args[0][0]
    assert attempt_call["score"] == 85.5


def test_save_audio_with_transcript(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs
    store._attempts_col = mock_attempts_col
    file_id = ObjectId()
    mock_gridfs.put.return_value = file_id

    file_obj = BytesIO(b"fake audio data")
    store.save_audio(file_obj, spell="Lumos", filename="test.wav", transcript="Lumos")
    call_args = mock_gridfs.put.call_args
    assert call_args[1]["metadata"]["transcript"] == "Lumos"
    attempt_call = mock_attempts_col.insert_one.call_args[0][0]
    assert attempt_call["transcript"] == "Lumos"

def test_delete_audio(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs
    store._attempts_col = mock_attempts_col
    file_id = ObjectId()
    store.delete_audio(file_id)

    mock_gridfs.delete.assert_called_once_with(file_id)
    mock_attempts_col.delete_many.assert_called_once_with({"audio_file_id": file_id})


def test_get_attempts_by_spell(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs
    store._attempts_col = mock_attempts_col
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = [
        {"spell": "Lumos", "score": 85.5},
        {"spell": "Lumos", "score": 90.0},
    ]
    mock_attempts_col.find.return_value = mock_cursor

    attempts = store.get_attempts_by_spell("Lumos")

    assert len(attempts) == 2
    assert attempts[0]["spell"] == "Lumos"
    mock_attempts_col.find.assert_called_once_with({"spell": "Lumos"})
    mock_cursor.sort.assert_called_once_with("recorded_at", -1)


def test_load_audio_to_file(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs
    store._attempts_col = mock_attempts_col
    file_id = ObjectId()
    mock_grid_out = MagicMock()
    mock_grid_out.read.return_value = b"audio data"
    mock_gridfs.get.return_value = mock_grid_out
    file_obj = BytesIO()
    store.load_audio_to_file(file_id, file_obj)
    mock_gridfs.get.assert_called_once_with(file_id)
    assert file_obj.getvalue() == b"audio data"