import sys
import os
os.environ["SPEECH_KEY"] = "fake_key"
os.environ["SPEECH_REGION"] = "fake_region"
from unittest.mock import MagicMock

sys.modules['audioop'] = MagicMock()
mock_pronun_assess = MagicMock()
sys.modules['pronun_assess'] = mock_pronun_assess
mock_pronun_assess.convert_to_wav = MagicMock()
mock_pronun_assess.pronunciation_assessment = MagicMock()
