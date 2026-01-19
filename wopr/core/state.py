"""State machine for WOPR application flow."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Any


class GameState(Enum):
    """Application states."""
    STARTUP = auto()
    DIAL_UP = auto()
    CONNECTED = auto()
    LOGIN = auto()
    AUTHENTICATE = auto()
    GREETING = auto()
    GAME_LIST = auto()
    GAME_SELECT = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    LEARNING = auto()  # Tic-tac-toe learning sequence
    WISDOM = auto()  # "A strange game..." finale
    EXIT = auto()


@dataclass
class StateContext:
    """Context data passed between states."""
    username: str = ""
    current_game: str | None = None
    game_instance: Any = None
    login_attempts: int = 0
    games_played: list[str] = field(default_factory=list)
    gtw_completed: bool = False

    def reset_game(self) -> None:
        """Reset game-related context."""
        self.current_game = None
        self.game_instance = None


class WOPRStateMachine:
    """State machine managing application flow."""

    # Valid state transitions
    TRANSITIONS: dict[GameState, set[GameState]] = {
        GameState.STARTUP: {GameState.DIAL_UP, GameState.GAME_LIST},  # skip_intro support
        GameState.DIAL_UP: {GameState.CONNECTED},
        GameState.CONNECTED: {GameState.LOGIN},
        GameState.LOGIN: {GameState.AUTHENTICATE},
        GameState.AUTHENTICATE: {GameState.LOGIN, GameState.GREETING},
        GameState.GREETING: {GameState.GAME_LIST},
        GameState.GAME_LIST: {GameState.GAME_SELECT, GameState.PLAYING, GameState.EXIT},
        GameState.GAME_SELECT: {GameState.PLAYING, GameState.GAME_LIST},
        GameState.PLAYING: {GameState.GAME_OVER, GameState.GAME_LIST, GameState.LEARNING},
        GameState.GAME_OVER: {GameState.GAME_LIST, GameState.LEARNING},
        GameState.LEARNING: {GameState.WISDOM},
        GameState.WISDOM: {GameState.GAME_LIST, GameState.EXIT},
        GameState.EXIT: set(),
    }

    def __init__(self) -> None:
        self._state = GameState.STARTUP
        self._context = StateContext()
        self._callbacks: dict[GameState, list[Callable[[StateContext], None]]] = {}
        self._transition_callbacks: list[Callable[[GameState, GameState, StateContext], None]] = []

    @property
    def state(self) -> GameState:
        """Current state."""
        return self._state

    @property
    def context(self) -> StateContext:
        """State context data."""
        return self._context

    def can_transition(self, target: GameState) -> bool:
        """Check if transition to target state is valid."""
        return target in self.TRANSITIONS.get(self._state, set())

    def transition(self, target: GameState) -> bool:
        """Transition to a new state if valid."""
        if not self.can_transition(target):
            return False

        old_state = self._state
        self._state = target

        # Notify transition callbacks
        for callback in self._transition_callbacks:
            callback(old_state, target, self._context)

        # Notify state-specific callbacks
        for callback in self._callbacks.get(target, []):
            callback(self._context)

        return True

    def on_state(self, state: GameState, callback: Callable[[StateContext], None]) -> None:
        """Register callback for when entering a specific state."""
        if state not in self._callbacks:
            self._callbacks[state] = []
        self._callbacks[state].append(callback)

    def on_transition(self, callback: Callable[[GameState, GameState, StateContext], None]) -> None:
        """Register callback for any state transition."""
        self._transition_callbacks.append(callback)

    def reset(self) -> None:
        """Reset state machine to initial state."""
        self._state = GameState.STARTUP
        self._context = StateContext()

    def is_terminal(self) -> bool:
        """Check if current state is terminal (no valid transitions)."""
        return len(self.TRANSITIONS.get(self._state, set())) == 0
