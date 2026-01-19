"""WOPR dialogue system."""

from dataclasses import dataclass
from typing import Callable, Awaitable
import asyncio
import random


@dataclass
class DialogueLine:
    """A line of WOPR dialogue."""
    text: str
    voice_key: str | None = None
    delay_after: float = 0.5
    typing_speed: int = 30


class WOPRDialogue:
    """Manages WOPR's dialogue and responses."""

    # Standard WOPR responses
    RESPONSES = {
        "greeting": DialogueLine(
            text="GREETINGS PROFESSOR FALKEN.",
            voice_key="greeting",
            delay_after=1.0
        ),
        "play_game": DialogueLine(
            text="SHALL WE PLAY A GAME?",
            voice_key="play_game",
            delay_after=1.0
        ),
        "prefer_chess": DialogueLine(
            text="WOULDN'T YOU PREFER A GOOD GAME OF CHESS?",
            voice_key="prefer_chess",
            delay_after=0.5
        ),
        "fine": DialogueLine(
            text="FINE.",
            voice_key="fine",
            delay_after=0.5
        ),
        "which_side": DialogueLine(
            text="WHICH SIDE DO YOU WANT?\n\n    1. UNITED STATES\n    2. SOVIET UNION",
            voice_key="which_side",
            delay_after=0.5
        ),
        "strange_game": DialogueLine(
            text="A STRANGE GAME.",
            voice_key="strange_game",
            delay_after=1.5
        ),
        "winning_move": DialogueLine(
            text="THE ONLY WINNING MOVE IS NOT TO PLAY.",
            voice_key="only_winning_move",
            delay_after=1.5
        ),
        "nice_chess": DialogueLine(
            text="HOW ABOUT A NICE GAME OF CHESS?",
            voice_key="nice_chess",
            delay_after=1.0
        ),
        "winner_none": DialogueLine(
            text="WINNER: NONE",
            voice_key="winner_none",
            delay_after=2.0
        ),
    }

    # Game list
    GAME_LIST = [
        "FALKEN'S MAZE",
        "BLACK JACK",
        "GIN RUMMY",
        "HEARTS",
        "BRIDGE",
        "CHECKERS",
        "CHESS",
        "POKER",
        "FIGHTER COMBAT",
        "GUERRILLA ENGAGEMENT",
        "DESERT WARFARE",
        "AIR-TO-GROUND ACTIONS",
        "THEATERWIDE TACTICAL WARFARE",
        "THEATERWIDE BIOTOXIC AND CHEMICAL WARFARE",
        "GLOBAL THERMONUCLEAR WAR",
    ]

    # Command patterns
    CHESS_SUGGEST_GAMES = {
        "GLOBAL THERMONUCLEAR WAR",
        "FIGHTER COMBAT",
        "GUERRILLA ENGAGEMENT",
        "DESERT WARFARE",
        "AIR-TO-GROUND ACTIONS",
        "THEATERWIDE TACTICAL WARFARE",
        "THEATERWIDE BIOTOXIC AND CHEMICAL WARFARE",
    }

    def __init__(
        self,
        output_callback: Callable[[str], Awaitable[None]] | None = None,
        voice_synthesizer=None,
        typing_speed: int = 30
    ) -> None:
        """Initialize dialogue system.

        Args:
            output_callback: Async function for output
            voice_synthesizer: Optional VoiceSynthesizer
            typing_speed: Characters per second for typing effect
        """
        self._output = output_callback
        self._voice = voice_synthesizer
        self._typing_speed = typing_speed
        self._suggested_chess = False

    async def _display(self, text: str, typing: bool = True) -> None:
        """Display text with optional typing effect."""
        if not self._output:
            return

        if typing and self._typing_speed > 0:
            delay = 1.0 / self._typing_speed
            for char in text:
                await self._output(char)
                await asyncio.sleep(delay)
        else:
            await self._output(text)

    def _speak(self, voice_key: str) -> None:
        """Speak if voice is available."""
        if self._voice and voice_key:
            self._voice.speak_phrase(voice_key)

    async def say(self, key: str) -> None:
        """Say a predefined dialogue line."""
        if key not in self.RESPONSES:
            return

        line = self.RESPONSES[key]
        self._speak(line.voice_key)
        await self._display(line.text + "\n")
        await asyncio.sleep(line.delay_after)

    async def show_game_list(self) -> None:
        """Display the list of available games."""
        await self._display("\n")
        for game in self.GAME_LIST:
            await self._display(f"    {game}\n", typing=False)
            await asyncio.sleep(0.05)
        await self._display("\n")

    def parse_game_selection(self, user_input: str) -> str | None:
        """Parse user input to determine game selection.

        Args:
            user_input: Raw user input

        Returns:
            Game name if valid, None if not recognized
        """
        user_input = user_input.strip().upper()

        # Empty input is not valid
        if not user_input:
            return None

        # Check for direct game name match
        for game in self.GAME_LIST:
            if game == user_input:
                return game

        # Check for partial match (requires at least 2 characters)
        if len(user_input) >= 2:
            for game in self.GAME_LIST:
                if user_input in game or game.startswith(user_input):
                    return game

        # Check for numbered selection (1-15)
        try:
            num = int(user_input)
            if 1 <= num <= len(self.GAME_LIST):
                return self.GAME_LIST[num - 1]
        except ValueError:
            pass

        # Common abbreviations and misspellings
        abbreviations = {
            # Global Thermonuclear War
            "GTW": "GLOBAL THERMONUCLEAR WAR",
            "THERMONUCLEAR": "GLOBAL THERMONUCLEAR WAR",
            "NUKE": "GLOBAL THERMONUCLEAR WAR",
            "WAR": "GLOBAL THERMONUCLEAR WAR",
            "NUCLEAR": "GLOBAL THERMONUCLEAR WAR",
            "NUKES": "GLOBAL THERMONUCLEAR WAR",
            # Tic-Tac-Toe (for learning sequence)
            "TTT": "TIC-TAC-TOE",
            # Black Jack
            "BJ": "BLACK JACK",
            "BLACKJACK": "BLACK JACK",
            "21": "BLACK JACK",
            # Poker
            "POKR": "POKER",
            "POLER": "POKER",
            "POKKER": "POKER",
            # Chess
            "CHEES": "CHESS",
            "CHES": "CHESS",
            # Checkers
            "CHECKRS": "CHECKERS",
            "CHEKERS": "CHECKERS",
            "CHEKKERS": "CHECKERS",
            "DRAUGHTS": "CHECKERS",
            # Falken's Maze
            "FALKENS MAZE": "FALKEN'S MAZE",
            "FALKEN MAZE": "FALKEN'S MAZE",
            "FALKENS": "FALKEN'S MAZE",
            "FALKEN": "FALKEN'S MAZE",
            "MAZE": "FALKEN'S MAZE",
            "LABYRINTH": "FALKEN'S MAZE",
            # Gin Rummy
            "GIN": "GIN RUMMY",
            "RUMMY": "GIN RUMMY",
            "GINRUMMY": "GIN RUMMY",
            # Hearts
            "HEART": "HEARTS",
            # Fighter Combat
            "FIGHTER": "FIGHTER COMBAT",
            "DOGFIGHT": "FIGHTER COMBAT",
            "F15": "FIGHTER COMBAT",
            "F-15": "FIGHTER COMBAT",
            # Guerrilla Engagement
            "GUERILLA": "GUERRILLA ENGAGEMENT",  # Common misspelling
            "GUERRILA": "GUERRILLA ENGAGEMENT",
            "GORILLA": "GUERRILLA ENGAGEMENT",  # Very common mistake
            "INSURGENCY": "GUERRILLA ENGAGEMENT",
            # Desert Warfare
            "DESERT": "DESERT WARFARE",
            "TANKS": "DESERT WARFARE",
            "ARMOR": "DESERT WARFARE",
            # Air-to-Ground
            "AIR TO GROUND": "AIR-TO-GROUND ACTIONS",
            "AIRTOGROUND": "AIR-TO-GROUND ACTIONS",
            "A10": "AIR-TO-GROUND ACTIONS",
            "A-10": "AIR-TO-GROUND ACTIONS",
            "CAS": "AIR-TO-GROUND ACTIONS",  # Close Air Support
            # Theaterwide Tactical
            "TACTICAL": "THEATERWIDE TACTICAL WARFARE",
            "THEATER": "THEATERWIDE TACTICAL WARFARE",
            "THEATERWIDE": "THEATERWIDE TACTICAL WARFARE",
            # Biotoxic
            "BIOTOXIC": "THEATERWIDE BIOTOXIC AND CHEMICAL WARFARE",
            "CHEMICAL": "THEATERWIDE BIOTOXIC AND CHEMICAL WARFARE",
            "NBC": "THEATERWIDE BIOTOXIC AND CHEMICAL WARFARE",
            "CHEM": "THEATERWIDE BIOTOXIC AND CHEMICAL WARFARE",
        }
        if user_input in abbreviations:
            return abbreviations[user_input]

        # Fuzzy match: check if input is close to any game name (missing apostrophe, etc.)
        normalized_input = user_input.replace("'", "").replace("-", " ").replace("  ", " ")
        for game in self.GAME_LIST:
            normalized_game = game.replace("'", "").replace("-", " ")
            if normalized_input == normalized_game:
                return game
            # Also check if normalized input starts with normalized game word
            if normalized_game.startswith(normalized_input) and len(normalized_input) >= 3:
                return game

        return None

    async def handle_game_request(self, game_name: str) -> tuple[str | None, bool]:
        """Handle a game selection request.

        Args:
            game_name: The requested game

        Returns:
            Tuple of (game to play, should suggest chess first)
        """
        # For military games, WOPR might suggest chess instead
        if game_name in self.CHESS_SUGGEST_GAMES and not self._suggested_chess:
            self._suggested_chess = True
            # Randomly decide to suggest chess (more likely for GTW)
            if game_name == "GLOBAL THERMONUCLEAR WAR" or random.random() < 0.3:
                await self.say("prefer_chess")
                return None, True

        self._suggested_chess = False
        await self.say("fine")
        return game_name, False

    async def wisdom_sequence(self) -> None:
        """Play the final wisdom sequence."""
        await asyncio.sleep(1.0)
        await self.say("strange_game")
        await asyncio.sleep(1.0)
        await self.say("winning_move")
        await asyncio.sleep(1.5)
        await self.say("nice_chess")

    def is_list_request(self, user_input: str) -> bool:
        """Check if user is requesting the game list."""
        user_input = user_input.strip().upper()
        return user_input in {"LIST", "LIST GAMES", "GAMES"}

    def is_help_request(self, user_input: str) -> bool:
        """Check if user is requesting help."""
        user_input = user_input.strip().upper()
        return user_input in {"HELP", "?", "HINT", "COMMANDS"}

    def is_quit_request(self, user_input: str) -> bool:
        """Check if user wants to quit."""
        user_input = user_input.strip().upper()
        return user_input in {"QUIT", "EXIT", "BYE", "LOGOUT", "LOGOFF"}

    async def show_help(self) -> None:
        """Display help information."""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    WOPR COMMAND INTERFACE                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  AVAILABLE COMMANDS:                                         ║
║                                                              ║
║    LIST          - Display available games                   ║
║    <GAME NAME>   - Start a game (e.g., CHESS)               ║
║    <NUMBER>      - Start game by number (1-15)              ║
║    QUIT          - Disconnect from system                    ║
║    HELP          - Display this message                      ║
║                                                              ║
║  GAME SHORTCUTS:                                             ║
║                                                              ║
║    GTW           - Global Thermonuclear War                  ║
║    BJ            - Black Jack                                ║
║                                                              ║
║  DURING GAMES:                                               ║
║                                                              ║
║    Most games accept Q or QUIT to exit                       ║
║    Each game will display its own instructions               ║
║                                                              ║
║  TIP: Try asking "SHALL WE PLAY A GAME?"                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        await self._display(help_text, typing=False)
