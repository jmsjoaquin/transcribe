from worker.app.services.stt.base import TranscriptionEngine
from worker.app.services.stt.faster_whisper_engine import FasterWhisperEngine


def get_transcription_engine() -> TranscriptionEngine:
    return FasterWhisperEngine()
