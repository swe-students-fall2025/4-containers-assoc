import sys
from unittest.mock import MagicMock

sys.modules['audioop'] = MagicMock()
mock_pronun_assess = MagicMock()
sys.modules['pronun_assess'] = mock_pronun_assess
mock_pronun_assess.convert_to_wav = MagicMock()
mock_pronun_assess.pronunciation_assessment = MagicMock()
