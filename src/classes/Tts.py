class TTS:
    """Simple text-to-speech stub for tests."""
    def tts_to_file(self, text: str, path: str) -> None:
        # create empty wav file placeholder
        import wave
        with wave.open(path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(b'')
