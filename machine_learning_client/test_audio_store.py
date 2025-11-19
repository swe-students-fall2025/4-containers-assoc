import os
from io import BytesIO
from unittest.mock import Mock, MagicMock, patch
import pytest
from bson import ObjectId
from audio_store import AudioStore

@pytest.fixture
def mock_mongo():
    with patch("audio_store.MongoClient") as mock_client_class, \
         patch("audio_store.GridFS") as mock_gridfs_class:

        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_attempts_col = Mock()
        mock_db.__getitem__.side_effect = lambda name: mock_attempts_col if name == "audio_attempts" else Mock()
        mock_client.__getitem__.return_value = mock_db
        mock_gridfs = Mock()
        mock_client_class.return_value = mock_client
        mock_gridfs_class.return_value = mock_gridfs
        yield mock_client, mock_db, mock_gridfs, mock_attempts_col


def test_init_success(mock_mongo):
    mock_client, mock_db, mock_gridfs, _ = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    assert store._client == mock_client
    assert store._db == mock_db
    mock_gridfs.assert_called_once_with(mock_db, collection="audio")


def test_init_with_custom_collection(mock_mongo):
    _, mock_db, mock_gridfs, _ = mock_mongo
    AudioStore("mongodb://localhost:27017", "test_db", collection="custom")
    mock_gridfs.assert_called_once_with(mock_db, collection="custom")


@pytest.mark.parametrize("mongo_uri,db_name", [
    ("", "test_db"),
    ("mongodb://localhost", ""),
    (None, "test_db"),
    ("mongodb://localhost", None)
])
@patch("audio_store.MongoClient")
@patch("audio_store.GridFS")
def test_init_raises_value_error(mock_gridfs, mock_mongo_client, mongo_uri, db_name):
    with pytest.raises(ValueError, match="MONGO_URI and DB_NAME must be provided"):
        AudioStore(mongo_uri, db_name)


@patch("audio_store.AudioStore.__init__")
@patch.dict(os.environ, {"MONGO_URI": "mongodb://localhost:27017", "DB_NAME": "test_db"})
def test_from_env_success(mock_init):
    mock_init.return_value = None
    AudioStore.from_env()
    mock_init.assert_called_once_with("mongodb://localhost:27017", "test_db", collection="audio")


@patch("audio_store.AudioStore.__init__")
@patch.dict(os.environ, {"MONGO_URI": "mongodb://localhost:27017", "DB_NAME": "test_db"})
def test_from_env_custom_collection(mock_init):
    mock_init.return_value = None
    AudioStore.from_env(collection="custom")
    mock_init.assert_called_once_with("mongodb://localhost:27017", "test_db", collection="custom")


@pytest.mark.parametrize("env_vars", [{}, {"MONGO_URI": "mongodb://localhost:27017"}])
def test_from_env_missing_vars(env_vars):
    with patch.dict(os.environ, env_vars, clear=True):
        with pytest.raises(ValueError, match="MONGO_URI and DB_NAME environment variables must be set"):
            AudioStore.from_env()


@pytest.fixture
def audio_store(mock_mongo):
    _, mock_db, mock_gridfs, _ = mock_mongo
    return AudioStore("mongodb://localhost:27017", "test_db")


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


def test_save_audio_with_score(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs

    file_id = ObjectId()
    mock_gridfs.put.return_value = file_id

    file_obj = BytesIO(b"fake audio data")
    result_id = store.save_audio(file_obj, spell="Lumos", filename="test.wav", score=85.5)

    assert result_id == file_id
    call_args = mock_gridfs.put.call_args
    assert call_args[1]["metadata"]["score"] == 85.5
    attempt_call = mock_attempts_col.insert_one.call_args[0][0]
    assert attempt_call["score"] == 85.5


def test_save_audio_with_transcript(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs

    file_id = ObjectId()
    mock_gridfs.put.return_value = file_id

    file_obj = BytesIO(b"fake audio data")
    result_id = store.save_audio(file_obj, spell="Lumos", filename="test.wav", transcript="Lumos")

    assert result_id == file_id
    call_args = mock_gridfs.put.call_args
    assert call_args[1]["metadata"]["transcript"] == "Lumos"
    attempt_call = mock_attempts_col.insert_one.call_args[0][0]
    assert attempt_call["transcript"] == "Lumos"


def test_save_audio_with_extra_metadata(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs

    file_id = ObjectId()
    mock_gridfs.put.return_value = file_id

    file_obj = BytesIO(b"fake audio data")
    extra_metadata = {"user_id": "123", "session_id": "abc"}
    result_id = store.save_audio(file_obj, spell="Lumos", filename="test.wav", extra_metadata=extra_metadata)

    assert result_id == file_id
    call_args = mock_gridfs.put.call_args
    assert call_args[1]["metadata"]["user_id"] == "123"
    assert call_args[1]["metadata"]["session_id"] == "abc"


def test_get_audio_success(audio_store):
    mock_fs = Mock()
    audio_store._fs = mock_fs

    file_id = ObjectId()
    mock_grid_out = Mock()
    mock_grid_out.read.return_value = b"audio bytes"
    mock_grid_out.metadata = {"spell": "Lumos", "filename": "test.wav"}
    mock_fs.get.return_value = mock_grid_out

    audio_bytes, metadata = audio_store.get_audio(file_id)

    assert audio_bytes == b"audio bytes"
    assert metadata["spell"] == "Lumos"
    assert metadata["filename"] == "test.wav"
    mock_fs.get.assert_called_once_with(file_id)


def test_get_audio_no_metadata(audio_store):
    mock_fs = Mock()
    audio_store._fs = mock_fs

    file_id = ObjectId()
    mock_grid_out = Mock()
    mock_grid_out.read.return_value = b"audio bytes"
    mock_grid_out.metadata = None
    mock_fs.get.return_value = mock_grid_out

    audio_bytes, metadata = audio_store.get_audio(file_id)

    assert audio_bytes == b"audio bytes"
    assert metadata == {}


def test_delete_audio(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")
    store._fs = mock_gridfs

    file_id = ObjectId()
    store.delete_audio(file_id)

    mock_gridfs.delete.assert_called_once_with(file_id)
    mock_attempts_col.delete_many.assert_called_once_with({"audio_file_id": file_id})


def test_get_attempts_by_spell(mock_mongo):
    _, mock_db, mock_gridfs, mock_attempts_col = mock_mongo
    store = AudioStore("mongodb://localhost:27017", "test_db")

    mock_cursor = Mock()
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


def test_load_audio_to_file(audio_store):
    mock_fs = Mock()
    audio_store._fs = mock_fs

    file_id = ObjectId()
    mock_grid_out = Mock()
    mock_grid_out.read.return_value = b"audio data"
    mock_fs.get.return_value = mock_grid_out

    file_obj = BytesIO()
    audio_store.load_audio_to_file(file_id, file_obj)

    mock_fs.get.assert_called_once_with(file_id)
    assert file_obj.getvalue() == b"audio data"