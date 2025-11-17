from azure.cognitiveservices.speech import SpeechConfig, AudioConfig
import azure.cognitiveservices.speech as speechsdk
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv
from pathlib import Path

# point to parent directory

load_dotenv()
KVUri = os.getenv("KV_URL")
speech_region = os.getenv("SPEECH_REGION")
secret_n = os.getenv("SECRET_NAME")
print("KVUri:", KVUri)
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

retrieved_secret = client.get_secret(secret_n)

# Now you can use the API key:

api_key = retrieved_secret.value
# print(f"The API key is: {api_key}")

def pronunciation_assessment(standard, user_audio):

    speech_config = SpeechConfig(subscription=api_key, region=speech_region)
    audio_config = AudioConfig(filename=user_audio) # this need to be changed to audio file from frontend
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language="en-US", audio_config=audio_config)

    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=standard,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=False)

    pronunciation_config.apply_to(speech_recognizer)

    # print("Speak now...")

    speech_recognition_result = speech_recognizer.recognize_once()

    # check recognition succeed
    print("Reason:", speech_recognition_result.reason)
    print("Recognized text:", speech_recognition_result.text)

    if speech_recognition_result.reason != speechsdk.ResultReason.RecognizedSpeech:
        return {
            "success": False,
            "error": f"Recognition failed: {speech_recognition_result.reason}",
        }

    # The pronunciation assessment result as a Speech SDK object
    result = speechsdk.PronunciationAssessmentResult(speech_recognition_result)

    # The pronunciation assessment result as a JSON string
    #result_json = speech_recognition_result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)

    print("Recognized text:", speech_recognition_result.text)
    print("Accuracy:", result.accuracy_score)
    #print("JSON:", result_json)

    return {
        "success": True,
        "recognized_text": speech_recognition_result.text,
        "accuracy_score": result.accuracy_score,
        "reference_text": standard,
    }