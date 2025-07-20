"""Minimal text-to-speech helper used in tests."""

class TTS:
    def synthesize(self, text: str, *, voice: str | None = None) -> str:
        """Return a dummy path for synthesized audio."""
        return f"/tmp/{hash(text)}.mp3"
