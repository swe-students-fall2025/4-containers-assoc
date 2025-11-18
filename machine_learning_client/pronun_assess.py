from azure.cognitiveservices.speech import SpeechConfig, AudioConfig
import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv
from pydub import AudioSegment

# point to parent directory

load_dotenv()

speech_region = os.getenv("SPEECH_REGION")
api_key = os.getenv("SPEECH_KEY")

if not api_key or not speech_region:
    raise RuntimeError("SPEECH_KEY and SPEECH_REGION must be set")

# print(f"The API key is: {api_key}")

def grade_from_score(score: float) -> dict:
    if score >= 70:
        return {"grade": "O", "label": "Outstanding", "color": "good"}
    elif score >= 40:
        return {"grade": "E", "label": "Exceeds Expectations", "color": "ok"}
    elif score >= 20:
        return {"grade": "A", "label": "Acceptable", "color": "warn"}
    else:
        return {"grade": "T", "label": "Troll", "color": "bad"}
    
def pronunciation_assessment(reference_text, user_audio):

    speech_config = SpeechConfig(subscription=api_key, region=speech_region)
    audio_config = AudioConfig(filename=user_audio) 
    # audio_config = AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language="en-US", audio_config=audio_config)

    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=False)

    pronunciation_config.apply_to(speech_recognizer)

    # print("Speak now...")

    speech_recognition_result = speech_recognizer.recognize_once()

    # check recognition succeed
    print("Reason:", speech_recognition_result.reason)
    print("Recognized text:", speech_recognition_result.text)

    if speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        no_match = speechsdk.NoMatchDetails.from_result(speech_recognition_result)
        print("NoMatch reason:", no_match.reason)
        return {
            "success": False,
            "error": f"No speech could be recognized ({no_match.reason})",
            "reference_text": reference_text,
        }

    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        details = speech_recognition_result.cancellation_details  # <-- use property, not from_result
        print("Canceled reason:", details.reason)
        print("Error details:", details.error_details or "")
        return {
            "success": False,
            "error": f"Recognition canceled: {details.reason}",
            "error_details": details.error_details,
            "reference_text": reference_text,
        }

    # The pronunciation assessment result as a Speech SDK object
    result = speechsdk.PronunciationAssessmentResult(speech_recognition_result)

    # The pronunciation assessment result as a JSON string
    #result_json = speech_recognition_result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)

    print("Recognized text:", speech_recognition_result.text)
    print("Accuracy:", result.accuracy_score)

    grade_info = grade_from_score(result.accuracy_score)

    return {
        "success": True,
        "recognized_text": speech_recognition_result.text,
        "accuracy_score": result.accuracy_score,
        "reference_text": reference_text,
        "grade": grade_info["grade"],
        "grade_label": grade_info["label"],
    }

def convert_to_wav(src_path: str) -> str:
    """
    Convert an audio file (e.g. webm/mp4) to PCM WAV and return the wav path.
    """
    wav_path = src_path + ".wav"
    audio = AudioSegment.from_file(src_path)
    audio = audio.set_frame_rate(16000).set_channels(1) 
    audio.export(wav_path, format="wav")
    return wav_path