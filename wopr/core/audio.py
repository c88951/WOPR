"""Sound effects manager for WOPR."""

from pathlib import Path
from typing import Optional
import threading


class AudioManager:
    """Manages sound effect playback.

    Supports multiple audio backends:
    - pygame (preferred, most portable)
    - simpleaudio (fallback)
    """

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
        self._backend = None  # 'pygame' or 'simpleaudio'
        self._initialized = False

        if enabled:
            self._init_audio()

    def _init_audio(self) -> None:
        """Initialize audio system, trying pygame first, then simpleaudio."""
        # Try pygame first (more portable)
        try:
            import pygame
            pygame.mixer.init()
            self._backend = 'pygame'
            self._initialized = True
            return
        except Exception:
            pass

        # Fallback to simpleaudio
        try:
            import simpleaudio
            self._backend = 'simpleaudio'
            self._initialized = True
            return
        except ImportError:
            pass

        # No audio backend available
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
            if self._backend == 'pygame':
                import pygame
                sound = pygame.mixer.Sound(str(sound_path))
                sound.set_volume(self._volume)
                self._cache[name] = sound
                return sound
            elif self._backend == 'simpleaudio':
                import simpleaudio
                wave_obj = simpleaudio.WaveObject.from_wave_file(str(sound_path))
                self._cache[name] = wave_obj
                return wave_obj
        except Exception:
            return None

        return None

    def play(self, sound_name: str, blocking: bool = False) -> None:
        """Play a sound effect."""
        if not self._enabled or not self._initialized:
            return

        sound_obj = self._load_sound(sound_name)
        if sound_obj is None:
            return

        try:
            if self._backend == 'pygame':
                channel = sound_obj.play()
                if blocking and channel:
                    import time
                    while channel.get_busy():
                        time.sleep(0.01)
            elif self._backend == 'simpleaudio':
                play_obj = sound_obj.play()
                if blocking:
                    play_obj.wait_done()
        except Exception:
            pass

    def stop(self, sound_name: str = None) -> None:
        """Stop a playing sound, or all sounds if no name given."""
        if not self._enabled or not self._initialized:
            return

        try:
            if self._backend == 'pygame':
                import pygame
                if sound_name and sound_name in self._cache:
                    self._cache[sound_name].stop()
                else:
                    pygame.mixer.stop()
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

    @property
    def backend(self) -> Optional[str]:
        """Return the active audio backend name."""
        return self._backend if self._initialized else None

    def set_volume(self, volume: float) -> None:
        """Set the volume (0.0 to 1.0)."""
        self._volume = max(0.0, min(1.0, volume))
        # Update volume for cached pygame sounds
        if self._backend == 'pygame':
            for sound in self._cache.values():
                try:
                    sound.set_volume(self._volume)
                except Exception:
                    pass

    def preload(self) -> None:
        """Preload all sound effects into cache."""
        for name in self.SOUNDS:
            self._load_sound(name)

    def cleanup(self) -> None:
        """Clean up audio resources."""
        if self._backend == 'pygame':
            try:
                import pygame
                pygame.mixer.quit()
            except Exception:
                pass
        self._cache.clear()
        self._initialized = False
