"""Scripted narrative sequences for WOPR."""

from typing import Callable, Awaitable
import asyncio

from .dialup import DialupSequence, QuickDialup
from .login import LoginHandler, LoginResult
from .dialogue import WOPRDialogue


class NarrativeSequences:
    """Manages the overall narrative flow of WOPR."""

    def __init__(
        self,
        output_callback: Callable[[str], Awaitable[None]],
        voice_synthesizer=None,
        audio_manager=None,
        skip_intro: bool = False,
        typing_speed: int = 30
    ) -> None:
        """Initialize narrative sequences.

        Args:
            output_callback: Async function for output
            voice_synthesizer: Optional voice synthesizer
            audio_manager: Optional audio manager
            skip_intro: Skip dialup sequence
            typing_speed: Characters per second
        """
        self._output = output_callback
        self._voice = voice_synthesizer
        self._audio = audio_manager
        self._skip_intro = skip_intro
        self._typing_speed = typing_speed

        # Initialize components
        self._dialup = (
            QuickDialup(output_callback) if skip_intro
            else DialupSequence(output_callback, audio_manager)
        )
        self._login = LoginHandler(output_callback, voice_synthesizer)
        self._dialogue = WOPRDialogue(output_callback, voice_synthesizer, typing_speed)

    async def _type_text(self, text: str, newline: bool = True) -> None:
        """Type text character by character."""
        if self._typing_speed <= 0:
            await self._output(text + ("\n" if newline else ""))
            return

        delay = 1.0 / self._typing_speed
        for char in text:
            await self._output(char)
            await asyncio.sleep(delay)
        if newline:
            await self._output("\n")

    async def run_dialup(self) -> bool:
        """Run the modem dialup sequence."""
        return await self._dialup.run()

    async def run_login(self, username: str) -> LoginResult:
        """Process a login attempt."""
        attempt = await self._login.attempt_login(username)
        return attempt.result

    async def run_greeting(self) -> None:
        """Run the greeting sequence after successful login."""
        await asyncio.sleep(0.5)
        await self._dialogue.say("greeting")
        await asyncio.sleep(0.5)
        await self._dialogue.say("play_game")

    async def show_game_list(self) -> None:
        """Display available games."""
        await self._dialogue.show_game_list()

    async def handle_game_selection(self, user_input: str) -> tuple[str | None, bool]:
        """Handle user's game selection input.

        Returns:
            Tuple of (selected game or None, should show chess suggestion)
        """
        # Check for help request
        if self._dialogue.is_help_request(user_input):
            await self._dialogue.show_help()
            return None, False

        # Check for list request
        if self._dialogue.is_list_request(user_input):
            await self.show_game_list()
            return None, False

        # Check for quit request
        if self._dialogue.is_quit_request(user_input):
            return "QUIT", False

        # Try to parse as game selection
        game = self._dialogue.parse_game_selection(user_input)
        if game:
            return await self._dialogue.handle_game_request(game)

        # Unknown command - give a hint about help
        await self._type_text("\nCOMMAND NOT RECOGNIZED. TYPE 'HELP' FOR ASSISTANCE.\n")
        return None, False

    async def run_gtw_intro(self, side: str) -> None:
        """Run the intro for Global Thermonuclear War."""
        await self._dialogue.say("which_side")

    async def run_winner_none(self) -> None:
        """Display WINNER: NONE message."""
        await self._dialogue.say("winner_none")

    async def run_learning_intro(self) -> None:
        """Introduce the learning sequence."""
        await self._type_text("\nA CURIOUS THING...\n")
        await asyncio.sleep(0.5)
        await self._type_text("LET ME DEMONSTRATE WITH A SIMPLER GAME.\n")
        await asyncio.sleep(1.0)
        await self._type_text("\nTIC-TAC-TOE\n")
        await asyncio.sleep(0.5)

    async def run_wisdom(self) -> None:
        """Run the final wisdom sequence."""
        await self._dialogue.wisdom_sequence()

    async def run_full_intro(self) -> bool:
        """Run the complete intro sequence (dialup + login prompt).

        Returns:
            True if completed successfully
        """
        # Dialup
        if not await self.run_dialup():
            return False

        return True

    def get_dialogue(self) -> WOPRDialogue:
        """Get the dialogue handler."""
        return self._dialogue
