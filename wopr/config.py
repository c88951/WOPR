"""Configuration management for WOPR."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
import sys
import os

# tomllib is Python 3.11+, use tomli as fallback
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@dataclass
class DisplayConfig:
    """Display settings."""
    typing_speed: int = 30  # Characters per second
    scanlines: bool = False  # CRT scanline effect
    animations: bool = True  # Enable/disable animations
    color_scheme: Literal["green", "amber", "white"] = "green"


@dataclass
class AudioConfig:
    """Audio settings."""
    enabled: bool = True
    voice_enabled: bool = True
    voice_rate: int = 140  # Words per minute
    sound_effects: bool = True
    volume: float = 0.8


@dataclass
class GameplayConfig:
    """Gameplay settings."""
    skip_intro: bool = False  # Jump to game list
    chess_difficulty: int = 3  # 1-5 scale
    save_games: bool = True  # Persist game state


@dataclass
class AccessibilityConfig:
    """Accessibility settings."""
    high_contrast: bool = False
    screen_reader_mode: bool = False  # Disable animations, verbose text


@dataclass
class WOPRConfig:
    """Main configuration container."""
    display: DisplayConfig = field(default_factory=DisplayConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    gameplay: GameplayConfig = field(default_factory=GameplayConfig)
    accessibility: AccessibilityConfig = field(default_factory=AccessibilityConfig)

    @classmethod
    def load(cls, config_path: Path | None = None) -> "WOPRConfig":
        """Load configuration from file."""
        if config_path is None:
            config_path = Path.home() / ".wopr" / "config.toml"

        if not config_path.exists():
            return cls()

        if tomllib is None:
            return cls()

        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)

            return cls(
                display=DisplayConfig(**data.get("display", {})),
                audio=AudioConfig(**data.get("audio", {})),
                gameplay=GameplayConfig(**data.get("gameplay", {})),
                accessibility=AccessibilityConfig(**data.get("accessibility", {})),
            )
        except Exception:
            return cls()

    def save(self, config_path: Path | None = None) -> None:
        """Save configuration to file."""
        if config_path is None:
            config_path = Path.home() / ".wopr" / "config.toml"

        config_path.parent.mkdir(parents=True, exist_ok=True)

        content = f'''[display]
typing_speed = {self.display.typing_speed}
scanlines = {str(self.display.scanlines).lower()}
animations = {str(self.display.animations).lower()}
color_scheme = "{self.display.color_scheme}"

[audio]
enabled = {str(self.audio.enabled).lower()}
voice_enabled = {str(self.audio.voice_enabled).lower()}
voice_rate = {self.audio.voice_rate}
sound_effects = {str(self.audio.sound_effects).lower()}
volume = {self.audio.volume}

[gameplay]
skip_intro = {str(self.gameplay.skip_intro).lower()}
chess_difficulty = {self.gameplay.chess_difficulty}
save_games = {str(self.gameplay.save_games).lower()}

[accessibility]
high_contrast = {str(self.accessibility.high_contrast).lower()}
screen_reader_mode = {str(self.accessibility.screen_reader_mode).lower()}
'''
        with open(config_path, "w") as f:
            f.write(content)


# Color schemes
COLOR_SCHEMES = {
    "green": {
        "primary": "#00FF00",
        "dim": "#006600",
        "bright": "#66FF66",
        "background": "#000000",
    },
    "amber": {
        "primary": "#FFB000",
        "dim": "#664400",
        "bright": "#FFCC66",
        "background": "#000000",
    },
    "white": {
        "primary": "#FFFFFF",
        "dim": "#666666",
        "bright": "#FFFFFF",
        "background": "#000000",
    },
}


# Application constants
APP_NAME = "WOPR"
APP_TITLE = "WOPR - WAR OPERATION PLAN RESPONSE"
APP_SUBTITLE = "NORAD COMPUTER SYSTEM"

# Paths
ASSETS_DIR = Path(__file__).parent / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
MAPS_DIR = ASSETS_DIR / "maps"
DATA_DIR = ASSETS_DIR / "data"
