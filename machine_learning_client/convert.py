from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import traceback

from audio_store import AudioStore 
from pronun_assess import convert_to_wav, pronunciation_assessment

app = FastAPI()
audio_store = AudioStore.from_env()

@app.post("/assess")
async def assess_pronunciation(
    spell: str = Form(...),
    audio: UploadFile = File(...),
):
    try:
        # 1) Save the uploaded audio into GridFS
        file_id = audio_store.save_audio(
            audio.file,
            spell=spell,
            filename=audio.filename,
            content_type=audio.content_type or "audio/webm",
        )

        # 2) Dump audio bytes from GridFS to a temp source file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_in:
            # write into the open file object
            audio_store.load_audio_to_file(file_id, tmp_in)
            input_path = tmp_in.name  # remember the path for later

        # 3) Convert that source file to WAV (Azure-friendly)
        wav_path = convert_to_wav(input_path)

        # 4) Run pronunciation assessment on the WAV file
        result = pronunciation_assessment(spell, wav_path)

        # 5) Clean up temp files
        for path in (input_path, wav_path):
            try:
                os.remove(path)
            except OSError:
                pass

        # 6) Include file_id in response
        result["file_id"] = str(file_id)

        return JSONResponse(
            content=result,
            status_code=200
            )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))