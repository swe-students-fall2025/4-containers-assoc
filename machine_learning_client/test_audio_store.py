import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from io import BytesIO
from bson import ObjectId
from audio_store import AudioStore

# Ensure environment variables for from_env
os.environ["MONGO_URI"] = "mongodb://localhost:27017"
os.environ["DB_NAME"] = "test_db"

@pytest.fixture
def mock_mongo():
    with patch("audio_store.MongoClient") as mock_client_class, \
         patch("audio_store.GridFS") as mock_gridfs_class:
         
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_gridfs_instance = MagicMock()
        mock_gridfs_class.return_value = mock_gridfs_instance
        mock_client_class.return_value = mock_client
        yield mock_client, mock_db, mock_gridfs_class, mock_gridfs_instance


def test_init_success(mock_mongo):
    mock_client, mock_db, mock_gridfs_class, mock_gridfs_instance = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    assert store._client == mock_client
    assert store._db == mock_db
    mock_gridfs_class.assert_called_once_with(mock_db, collection="audio")


def test_save_audio_basic(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs

    file_id = ObjectId()
    mock_gridfs.put.return_value = file_id

    file_obj = BytesIO(b"fake audio data")
    result_id = store.save_audio(file_obj, spell="Lumos", filename="test.wav", content_type="audio/wav")

    assert result_id == file_id
    mock_gridfs.put.assert_called_once()
    call_args = mock_gridfs.put.call_args
    assert call_args[1]["metadata"]["spell"] == "Lumos"
    mock_attempts_col.insert_one.assert_called_once()

