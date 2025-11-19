import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
import tempfile
from unittest.mock import Mock, patch
import pytest

os.environ.setdefault("SPEECH_KEY", "test_key")
os.environ.setdefault("SPEECH_REGION", "test_region")

from ..pronun_assess import pronunciation_assessment, grade_from_score, convert_to_wav


@pytest.mark.parametrize(
    "score,expected_grade,expected_label,expected_color",
    [
        (100.0, "O", "Outstanding", "good"),
        (85.5, "O", "Outstanding", "good"),
        (70.0, "O", "Outstanding", "good"),
        (69.9, "E", "Exceeds Expectations", "ok"),
        (55.5, "E", "Exceeds Expectations", "ok"),
        (40.0, "E", "Exceeds Expectations", "ok"),
        (39.9, "A", "Acceptable", "warn"),
        (30.0, "A", "Acceptable", "warn"),
        (20.0, "A", "Acceptable", "warn"),
        (19.9, "T", "Troll", "bad"),
        (10.5, "T", "Troll", "bad"),
        (0.0, "T", "Troll", "bad"),
    ],
)
def test_grade_from_score(score, expected_grade, expected_label, expected_color):
    result = grade_from_score(score)
    assert result["grade"] == expected_grade
    assert result["label"] == expected_label
    assert result["color"] == expected_color


@patch("machine_learning_client.pronun_assess.AudioSegment")
def test_convert_to_wav(mock_audio_segment):
    mock_audio = Mock()
    mock_audio.set_frame_rate.return_value = mock_audio
    mock_audio.set_channels.return_value = mock_audio
    mock_audio_segment.from_file.return_value = mock_audio

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
        src_path = tmp_file.name

    try:
        result_path = convert_to_wav(src_path)
        assert result_path == src_path + ".wav"
        mock_audio_segment.from_file.assert_called_once_with(src_path)
        mock_audio.set_frame_rate.assert_called_once_with(16000)
        mock_audio.set_channels.assert_called_once_with(1)
        mock_audio.export.assert_called_once_with(result_path, format="wav")
    finally:
        for path in [src_path, src_path + ".wav"]:
            if os.path.exists(path):
                os.remove(path)


@patch("machine_learning_client.pronun_assess.speechsdk")
@patch("machine_learning_client.pronun_assess.SpeechConfig")
@patch("machine_learning_client.pronun_assess.AudioConfig")
def test_pronunciation_assessment_success(mock_audio_config, mock_speech_config, mock_speechsdk):
    mock_result = Mock()
    mock_result.reason = mock_speechsdk.ResultReason.RecognizedSpeech
    mock_result.text = "Lumos"

    mock_assessment = Mock()
    mock_assessment.accuracy_score = 85.5

    mock_recognizer = Mock()
    mock_recognizer.recognize_once.return_value = mock_result
    mock_speechsdk.SpeechRecognizer.return_value = mock_recognizer
    mock_speechsdk.PronunciationAssessmentResult.return_value = mock_assessment

    result = pronunciation_assessment("Lumos", "/path/to/audio.wav")

    assert result["success"] is True
    assert result["recognized_text"] == "Lumos"
    assert result["accuracy_score"] == 85.5
    assert result["grade"] == "O"


@patch("machine_learning_client.pronun_assess.speechsdk")
@patch("machine_learning_client.pronun_assess.SpeechConfig")
@patch("machine_learning_client.pronun_assess.AudioConfig")
def test_pronunciation_assessment_no_match(mock_audio_config, mock_speech_config, mock_speechsdk):
    mock_result = Mock()
    mock_result.reason = mock_speechsdk.ResultReason.NoMatch

    mock_no_match = Mock()
    mock_no_match.reason = "InitialSilenceTimeout"
    mock_speechsdk.NoMatchDetails.from_result.return_value = mock_no_match

    mock_recognizer = Mock()
    mock_recognizer.recognize_once.return_value = mock_result
    mock_speechsdk.SpeechRecognizer.return_value = mock_recognizer

    result = pronunciation_assessment("Lumos", "/path/to/audio.wav")

    assert result["success"] is False
    assert "No speech could be recognized" in result["error"]


@patch("machine_learning_client.pronun_assess.speechsdk")
@patch("machine_learning_client.pronun_assess.SpeechConfig")
@patch("machine_learning_client.pronun_assess.AudioConfig")
def test_pronunciation_assessment_canceled(mock_audio_config, mock_speech_config, mock_speechsdk):
    mock_result = Mock()
    mock_result.reason = mock_speechsdk.ResultReason.Canceled

    mock_cancel_details = Mock()
    mock_cancel_details.reason = "Error"
    mock_cancel_details.error_details = "Connection timeout"
    mock_result.cancellation_details = mock_cancel_details

    mock_recognizer = Mock()
    mock_recognizer.recognize_once.return_value = mock_result
    mock_speechsdk.SpeechRecognizer.return_value = mock_recognizer

    result = pronunciation_assessment("Lumos", "/path/to/audio.wav")

    assert result["success"] is False
    assert "Recognition canceled" in result["error"]
    assert result["error_details"] == "Connection timeout"


@pytest.mark.parametrize("score,expected_grade,expected_label", [
    (90.0, "O", "Outstanding"),
    (50.0, "E", "Exceeds Expectations"),
    (30.0, "A", "Acceptable"),
    (10.0, "T", "Troll"),
])
@patch("machine_learning_client.pronun_assess.speechsdk")
@patch("machine_learning_client.pronun_assess.SpeechConfig")
@patch("machine_learning_client.pronun_assess.AudioConfig")
def test_pronunciation_assessment_different_grades(
    mock_audio_config, mock_speech_config, mock_speechsdk, score, expected_grade, expected_label
):
    mock_result = Mock()
    mock_result.reason = mock_speechsdk.ResultReason.RecognizedSpeech
    mock_result.text = "Test"

    mock_assessment = Mock()
    mock_assessment.accuracy_score = score

    mock_recognizer = Mock()
    mock_recognizer.recognize_once.return_value = mock_result
    mock_speechsdk.SpeechRecognizer.return_value = mock_recognizer
    mock_speechsdk.PronunciationAssessmentResult.return_value = mock_assessment

    result = pronunciation_assessment("Test", "/path/to/audio.wav")

    assert result["success"] is True
    assert result["grade"] == expected_grade
    assert result["grade_label"] == expected_label
    assert result["accuracy_score"] == score
