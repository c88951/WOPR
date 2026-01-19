"""Base game class for all WOPR games."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Awaitable, Any
from enum import Enum, auto


class GameResult(Enum):
    """Possible game outcomes."""
    WIN = auto()
    LOSE = auto()
    DRAW = auto()
    QUIT = auto()
    NONE = auto()  # For games like GTW where there's no winner


@dataclass
class GameOutcome:
    """Result of a completed game."""
    result: GameResult
    player_score: int = 0
    opponent_score: int = 0
    message: str = ""
    extra_data: dict[str, Any] = field(default_factory=dict)


class BaseGame(ABC):
    """Abstract base class for all games."""

    # Game metadata
    NAME: str = "UNKNOWN GAME"
    DESCRIPTION: str = ""
    INSTRUCTIONS: str = ""

    def __init__(
        self,
        output_callback: Callable[[str], Awaitable[None]],
        input_callback: Callable[[], Awaitable[str]],
        voice=None,
        audio=None,
    ) -> None:
        """Initialize the game.

        Args:
            output_callback: Async function to display text
            input_callback: Async function to get user input
            voice: Optional VoiceSynthesizer
            audio: Optional AudioManager
        """
        self._output = output_callback
        self._input = input_callback
        self._voice = voice
        self._audio = audio
        self._running = False

    async def output(self, text: str) -> None:
        """Display text to the user."""
        await self._output(text)

    async def input(self, prompt: str = "") -> str:
        """Get input from the user."""
        if prompt:
            await self._output(prompt)
        return await self._input()

    async def play_sound(self, sound_name: str) -> None:
        """Play a sound effect."""
        if self._audio:
            self._audio.play_async(sound_name)

    def speak(self, text: str) -> None:
        """Speak text using voice synthesis."""
        if self._voice:
            self._voice.speak(text)

    async def show_instructions(self) -> None:
        """Display game instructions."""
        if self.INSTRUCTIONS:
            await self.output(f"\n{self.INSTRUCTIONS}\n\n")

    @abstractmethod
    async def play(self) -> dict[str, Any]:
        """Play the game.

        Returns:
            Dictionary with game results and any extra data
        """
        pass

    async def quit(self) -> GameOutcome:
        """Handle quitting the game."""
        self._running = False
        return GameOutcome(result=GameResult.QUIT, message="GAME TERMINATED")


class CardGame(BaseGame):
    """Base class for card games."""

    SUITS = ["♠", "♥", "♦", "♣"]
    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._deck: list[tuple[str, str]] = []
        self._shuffle_deck()

    def _shuffle_deck(self) -> None:
        """Create and shuffle a new deck."""
        import random
        self._deck = [(rank, suit) for suit in self.SUITS for rank in self.RANKS]
        random.shuffle(self._deck)

    def _draw_card(self) -> tuple[str, str] | None:
        """Draw a card from the deck."""
        if self._deck:
            return self._deck.pop()
        return None

    def _card_str(self, card: tuple[str, str]) -> str:
        """Convert a card to string representation."""
        return f"{card[0]}{card[1]}"

    def _hand_str(self, hand: list[tuple[str, str]]) -> str:
        """Convert a hand to string representation."""
        return " ".join(self._card_str(card) for card in hand)

    def _render_card_art(self, card: tuple[str, str] | None, hidden: bool = False) -> list[str]:
        """Render a single card as ASCII art (5 lines)."""
        if hidden or card is None:
            return [
                "┌───────┐",
                "│░░░░░░░│",
                "│░░░░░░░│",
                "│░░░░░░░│",
                "└───────┘",
            ]

        rank, suit = card
        # Handle 10 which is 2 chars
        if rank == "10":
            top = f"│{rank}     │"
            bot = f"│     {rank}│"
        else:
            top = f"│{rank}      │"
            bot = f"│      {rank}│"

        return [
            "┌───────┐",
            top,
            f"│   {suit}   │",
            bot,
            "└───────┘",
        ]

    def _render_hand_art(
        self,
        hand: list[tuple[str, str]],
        numbered: bool = False,
        hidden_indices: set[int] | None = None
    ) -> str:
        """Render a hand as larger ASCII art cards.

        Args:
            hand: List of cards to render
            numbered: If True, show position numbers above cards
            hidden_indices: Set of indices to show as hidden cards
        """
        if not hand:
            return ""

        hidden_indices = hidden_indices or set()

        # Render each card
        card_renders = []
        for i, card in enumerate(hand):
            is_hidden = i in hidden_indices
            card_renders.append(self._render_card_art(card, hidden=is_hidden))

        # Combine horizontally with spacing
        lines = []

        # Position numbers if requested
        if numbered:
            num_line = "  ".join(f"    {i + 1}    " for i in range(len(hand)))
            lines.append(num_line)

        for row in range(5):
            line = "  ".join(render[row] for render in card_renders)
            lines.append(line)

        return "\n".join(lines)


class BoardGame(BaseGame):
    """Base class for board games."""

    BOARD_SIZE: int = 8

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._board: list[list[str]] = []
        self._init_board()

    def _init_board(self) -> None:
        """Initialize the game board."""
        self._board = [
            ["." for _ in range(self.BOARD_SIZE)]
            for _ in range(self.BOARD_SIZE)
        ]

    def _render_board(self) -> str:
        """Render the board as ASCII art."""
        lines = []
        # Column headers
        lines.append("  " + " ".join(chr(ord("A") + i) for i in range(self.BOARD_SIZE)))
        # Board rows
        for i, row in enumerate(self._board):
            lines.append(f"{i + 1} " + " ".join(row))
        return "\n".join(lines)
