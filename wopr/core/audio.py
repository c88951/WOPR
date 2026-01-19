"""Sound effects manager for WOPR."""

from pathlib import Path
from typing import Optional
import threading


class AudioManager:
    """Manages sound effect playback."""

    # Sound effect definitions
    SOUNDS = {
        "modem_dial": "modem_dial.wav",
        "modem_connect": "modem_connect.wav",
        "terminal_beep": "terminal_beep.wav",
        "keystroke": "typing.wav",
        "missile_launch": "missile_launch.wav",
        "explosion": "explosion.wav",
        "defcon_change": "defcon_change.wav",
    }

    def __init__(self, sounds_dir: Path, enabled: bool = True, volume: float = 0.8) -> None:
        self._sounds_dir = sounds_dir
        self._enabled = enabled
        self._volume = volume
        self._cache: dict[str, object] = {}
        self._simpleaudio = None
        self._initialized = False

        if enabled:
            self._init_audio()

    def _init_audio(self) -> None:
        """Initialize audio system."""
        try:
            import simpleaudio
            self._simpleaudio = simpleaudio
            self._initialized = True
        except ImportError:
            self._enabled = False
            self._initialized = False

    def _load_sound(self, name: str) -> Optional[object]:
        """Load a sound file into cache."""
        if name in self._cache:
            return self._cache[name]

        if name not in self.SOUNDS:
            return None

        sound_path = self._sounds_dir / self.SOUNDS[name]
        if not sound_path.exists():
            return None

        try:
            wave_obj = self._simpleaudio.WaveObject.from_wave_file(str(sound_path))
            self._cache[name] = wave_obj
            return wave_obj
        except Exception:
            return None

    def play(self, sound_name: str, blocking: bool = False) -> None:
        """Play a sound effect."""
        if not self._enabled or not self._initialized:
            return

        wave_obj = self._load_sound(sound_name)
        if wave_obj is None:
            return

        try:
            play_obj = wave_obj.play()
            if blocking:
                play_obj.wait_done()
        except Exception:
            pass

    def play_async(self, sound_name: str) -> None:
        """Play a sound effect in a background thread."""
        if not self._enabled or not self._initialized:
            return

        thread = threading.Thread(target=self.play, args=(sound_name,), daemon=True)
        thread.start()

    @property
    def enabled(self) -> bool:
        """Whether audio is enabled."""
        return self._enabled and self._initialized

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable audio."""
        self._enabled = value
        if value and not self._initialized:
            self._init_audio()

    def preload(self) -> None:
        """Preload all sound effects into cache."""
        for name in self.SOUNDS:
            self._load_sound(name)
