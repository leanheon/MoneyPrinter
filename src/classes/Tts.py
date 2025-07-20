class TTS:
    """Simple stub TTS class for tests."""

    def generate_audio(self, text: str) -> str:
        """Return path to generated audio (stub)."""
        return f"audio_{hash(text)}.mp3"
