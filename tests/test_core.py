"""Tests for core modules."""

import pytest
from wopr.core.state import GameState, WOPRStateMachine, StateContext
from wopr.config import WOPRConfig, DisplayConfig, AudioConfig


class TestStateMachine:
    """Tests for state machine."""

    def test_initial_state(self):
        """Test initial state is STARTUP."""
        sm = WOPRStateMachine()
        assert sm.state == GameState.STARTUP

    def test_valid_transition(self):
        """Test valid state transitions."""
        sm = WOPRStateMachine()

        assert sm.can_transition(GameState.DIAL_UP)
        assert sm.transition(GameState.DIAL_UP)
        assert sm.state == GameState.DIAL_UP

        assert sm.transition(GameState.CONNECTED)
        assert sm.state == GameState.CONNECTED

    def test_invalid_transition(self):
        """Test invalid state transitions are rejected."""
        sm = WOPRStateMachine()

        # Can't go directly from STARTUP to PLAYING
        assert not sm.can_transition(GameState.PLAYING)
        assert not sm.transition(GameState.PLAYING)
        assert sm.state == GameState.STARTUP

    def test_full_flow(self):
        """Test complete state flow."""
        sm = WOPRStateMachine()

        # Simulate full login flow
        assert sm.transition(GameState.DIAL_UP)
        assert sm.transition(GameState.CONNECTED)
        assert sm.transition(GameState.LOGIN)
        assert sm.transition(GameState.AUTHENTICATE)
        assert sm.transition(GameState.GREETING)
        assert sm.transition(GameState.GAME_LIST)
        assert sm.transition(GameState.PLAYING)

        assert sm.state == GameState.PLAYING

    def test_state_callbacks(self):
        """Test state change callbacks."""
        sm = WOPRStateMachine()
        callback_states = []

        def on_connected(ctx):
            callback_states.append("connected")

        def on_login(ctx):
            callback_states.append("login")

        sm.on_state(GameState.CONNECTED, on_connected)
        sm.on_state(GameState.LOGIN, on_login)

        sm.transition(GameState.DIAL_UP)
        sm.transition(GameState.CONNECTED)
        sm.transition(GameState.LOGIN)

        assert callback_states == ["connected", "login"]

    def test_transition_callback(self):
        """Test transition callbacks."""
        sm = WOPRStateMachine()
        transitions = []

        def on_transition(old, new, ctx):
            transitions.append((old, new))

        sm.on_transition(on_transition)

        sm.transition(GameState.DIAL_UP)
        sm.transition(GameState.CONNECTED)

        assert transitions == [
            (GameState.STARTUP, GameState.DIAL_UP),
            (GameState.DIAL_UP, GameState.CONNECTED),
        ]

    def test_context(self):
        """Test state context."""
        sm = WOPRStateMachine()

        sm.context.username = "joshua"
        sm.context.current_game = "CHESS"

        assert sm.context.username == "joshua"
        assert sm.context.current_game == "CHESS"

    def test_reset(self):
        """Test state machine reset."""
        sm = WOPRStateMachine()

        sm.transition(GameState.DIAL_UP)
        sm.context.username = "test"

        sm.reset()

        assert sm.state == GameState.STARTUP
        assert sm.context.username == ""


class TestConfig:
    """Tests for configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = WOPRConfig()

        assert config.display.typing_speed == 30
        assert config.display.color_scheme == "green"
        assert config.audio.enabled is True
        assert config.gameplay.chess_difficulty == 3

    def test_config_modification(self):
        """Test modifying configuration."""
        config = WOPRConfig()

        config.display.typing_speed = 50
        config.audio.enabled = False

        assert config.display.typing_speed == 50
        assert config.audio.enabled is False

    def test_display_config(self):
        """Test display configuration."""
        display = DisplayConfig(
            typing_speed=60,
            scanlines=True,
            animations=False,
            color_scheme="amber"
        )

        assert display.typing_speed == 60
        assert display.scanlines is True
        assert display.animations is False
        assert display.color_scheme == "amber"

    def test_audio_config(self):
        """Test audio configuration."""
        audio = AudioConfig(
            enabled=False,
            voice_enabled=True,
            voice_rate=120,
            volume=0.5
        )

        assert audio.enabled is False
        assert audio.voice_enabled is True
        assert audio.voice_rate == 120
        assert audio.volume == 0.5
