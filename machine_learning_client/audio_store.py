"""Audio storage utilities using MongoDB GridFS."""

import os
from datetime import datetime, timezone
from typing import BinaryIO, Dict, Optional

from bson import ObjectId  # pylint: disable=import-error
from dotenv import load_dotenv  # pylint: disable=import-error
from gridfs import GridFS  # pylint: disable=import-error
from pymongo import MongoClient  # pylint: disable=import-error

load_dotenv()


class AudioStore:
    """Store and retrieve audio files using MongoDB GridFS."""

    def __init__(self, mongo_uri: str, db_name: str, collection: str = "audio"):
        """Initialize the audio store."""
        if not mongo_uri or not db_name:
            raise ValueError("MONGO_URI and DB_NAME must be provided")
        self._client = MongoClient(mongo_uri, tz_aware=True)
        self._db = self._client[db_name]
        self._fs = GridFS(self._db, collection=collection)
        self._attempts_col = self._db["pronunciation_attempts"]

    @classmethod
    def from_env(cls, collection: str = "audio"):
        """Create AudioStore instance from environment variables."""
        mongo_uri = os.getenv("MONGO_URI")
        db_name = os.getenv("DB_NAME")
        if not mongo_uri or not db_name:
            raise ValueError("MONGO_URI and DB_NAME environment variables must be set")
        return cls(mongo_uri, db_name, collection=collection)

    def save_audio(  # pylint: disable=too-many-arguments
        self,
        file_obj: BinaryIO,
        *,
        spell: str,
        filename: str,
        content_type: str = "audio/wav",
        score: Optional[float] = None,
        transcript: Optional[str] = None,
        extra_metadata: Optional[Dict[str, object]] = None,
    ):
        """Save audio file to GridFS and record attempt metadata."""
        metadata: Dict[str, object] = {
            "spell": spell,
            "filename": filename,
            "content_type": content_type,
            "uploaded_at": datetime.now(tz=timezone.utc),
        }
        if score is not None:
            metadata["score"] = score
        if transcript:
            metadata["transcript"] = transcript
        if extra_metadata:
            metadata.update(extra_metadata)

        # Store audio in GridFS
        file_id = self._fs.put(
            file_obj,
            filename=filename,
            content_type=content_type,
            metadata=metadata,
        )

        # Record attempt in pronunciation_attempts collection
        attempt_doc = {
            "spell": spell,
            "audio_file_id": file_id,
            "recorded_at": metadata["uploaded_at"],
        }
        if score is not None:
            attempt_doc["score"] = score
        if transcript:
            attempt_doc["transcript"] = transcript

        self._attempts_col.insert_one(attempt_doc)

        return file_id

    def get_audio(self, file_id: ObjectId):
        """Retrieve audio file from GridFS."""
        grid_out = self._fs.get(file_id)
        audio_bytes = grid_out.read()
        metadata = grid_out.metadata or {}
        return audio_bytes, metadata

    def delete_audio(self, file_id: ObjectId):
        """Delete audio file from GridFS and related attempt records."""
        self._fs.delete(file_id)
        self._attempts_col.delete_many({"audio_file_id": file_id})

    def get_attempts_by_spell(self, spell: str):
        """Get all pronunciation attempts for a specific spell."""
        return list(self._attempts_col.find({"spell": spell}).sort("recorded_at", -1))
