"""Text-to-speech voice synthesis for WOPR."""

from typing import Callable
import threading
import queue


class VoiceSynthesizer:
    """Cross-platform text-to-speech wrapper."""

    # Key phrases that WOPR speaks
    PHRASES = {
        "greeting": "Greetings Professor Falken.",
        "play_game": "Shall we play a game?",
        "prefer_chess": "Wouldn't you prefer a good game of chess?",
        "strange_game": "A strange game.",
        "only_winning_move": "The only winning move is not to play.",
        "nice_chess": "How about a nice game of chess?",
        "winner_none": "Winner: None.",
        "fine": "Fine.",
        "which_side": "Which side do you want?",
    }

    def __init__(self, enabled: bool = True, rate: int = 140) -> None:
        self._enabled = enabled
        self._rate = rate
        self._engine = None
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._thread: threading.Thread | None = None
        self._running = False
        self._initialized = False

        if enabled:
            self._init_engine()

    def _init_engine(self) -> None:
        """Initialize the TTS engine."""
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self._rate)

            # Try to select a more robotic voice
            voices = self._engine.getProperty("voices")
            if voices:
                # Prefer male voices for WOPR's character
                for voice in voices:
                    if "male" in voice.name.lower():
                        self._engine.setProperty("voice", voice.id)
                        break

            self._initialized = True
        except Exception:
            self._enabled = False
            self._initialized = False

    def _worker(self) -> None:
        """Background worker for speech synthesis."""
        while self._running:
            try:
                text = self._queue.get(timeout=0.1)
                if text is None:
                    break
                if self._engine and self._enabled:
                    self._engine.say(text)
                    self._engine.runAndWait()
            except queue.Empty:
                continue
            except Exception:
                continue

    def start(self) -> None:
        """Start the voice synthesis worker thread."""
        if not self._enabled or not self._initialized:
            return

        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the voice synthesis worker thread."""
        self._running = False
        self._queue.put(None)  # Signal to stop
        if self._thread:
            self._thread.join(timeout=1.0)

    def speak(self, text: str) -> None:
        """Queue text for speech synthesis."""
        if self._enabled and self._initialized:
            self._queue.put(text)

    def speak_phrase(self, phrase_key: str) -> None:
        """Speak a predefined phrase by key."""
        if phrase_key in self.PHRASES:
            self.speak(self.PHRASES[phrase_key])

    @property
    def enabled(self) -> bool:
        """Whether voice synthesis is enabled."""
        return self._enabled and self._initialized

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable voice synthesis."""
        self._enabled = value
        if value and not self._initialized:
            self._init_engine()

    def set_rate(self, rate: int) -> None:
        """Set speech rate in words per minute."""
        self._rate = rate
        if self._engine:
            self._engine.setProperty("rate", rate)
