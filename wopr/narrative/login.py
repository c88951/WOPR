"""Login handler for WOPR."""

from typing import Callable, Awaitable
from dataclasses import dataclass
from enum import Enum, auto


class LoginResult(Enum):
    """Result of a login attempt."""
    INVALID = auto()
    BACKDOOR = auto()
    NORMAL = auto()
    HELP = auto()


@dataclass
class LoginAttempt:
    """Represents a login attempt."""
    username: str
    result: LoginResult
    message: str


class LoginHandler:
    """Handles user login/authentication for WOPR."""

    # Valid backdoor passwords
    BACKDOOR_NAMES = {"joshua", "Joshua", "JOSHUA"}

    # Help commands
    HELP_COMMANDS = {"help", "HELP", "?", "hint", "HINT"}

    # Messages
    MSG_INVALID = "IDENTIFICATION NOT RECOGNIZED"
    MSG_GREETING = "GREETINGS PROFESSOR FALKEN."
    MSG_PROMPT = "LOGON: "

    # Hidden help text (in-character as system documentation)
    MSG_HELP = """
╔══════════════════════════════════════════════════════════════╗
║            WOPR SYSTEM DOCUMENTATION - CLASSIFIED            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  AUTHENTICATION REQUIRED                                     ║
║                                                              ║
║  This system was developed by Dr. Stephen Falken at         ║
║  NORAD for strategic war simulations.                       ║
║                                                              ║
║  Standard access credentials are restricted to              ║
║  authorized military personnel only.                        ║
║                                                              ║
║  NOTE: Dr. Falken included a personal access method         ║
║  using a name significant to him - that of his son          ║
║  who died at an early age.                                  ║
║                                                              ║
║  For assistance, contact NORAD Systems Administration.      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

    def __init__(
        self,
        output_callback: Callable[[str], Awaitable[None]] | None = None,
        voice_synthesizer=None,
        max_attempts: int = 0  # 0 = unlimited
    ) -> None:
        """Initialize login handler.

        Args:
            output_callback: Async function for output
            voice_synthesizer: Optional VoiceSynthesizer for speech
            max_attempts: Maximum login attempts (0 = unlimited)
        """
        self._output = output_callback
        self._voice = voice_synthesizer
        self._max_attempts = max_attempts
        self._attempt_count = 0

    async def _display(self, text: str) -> None:
        """Display text if callback is set."""
        if self._output:
            await self._output(text)

    def _speak(self, phrase_key: str) -> None:
        """Speak a phrase if voice is available."""
        if self._voice:
            self._voice.speak_phrase(phrase_key)

    def validate(self, username: str) -> LoginAttempt:
        """Validate a login attempt.

        Args:
            username: The username/password entered

        Returns:
            LoginAttempt with result and message
        """
        username = username.strip()

        # Check for help request (doesn't count as attempt)
        if username in self.HELP_COMMANDS:
            return LoginAttempt(
                username=username,
                result=LoginResult.HELP,
                message=self.MSG_HELP
            )

        self._attempt_count += 1

        if username in self.BACKDOOR_NAMES:
            return LoginAttempt(
                username=username,
                result=LoginResult.BACKDOOR,
                message=self.MSG_GREETING
            )

        return LoginAttempt(
            username=username,
            result=LoginResult.INVALID,
            message=self.MSG_INVALID
        )

    async def attempt_login(self, username: str) -> LoginAttempt:
        """Process a login attempt with output.

        Args:
            username: The username/password entered

        Returns:
            LoginAttempt with result and message
        """
        attempt = self.validate(username)

        if attempt.result == LoginResult.BACKDOOR:
            # Successful backdoor access
            await self._display(f"\n{attempt.message}\n\n")
            self._speak("greeting")
        elif attempt.result == LoginResult.HELP:
            # Display help
            await self._display(attempt.message)
        else:
            # Invalid login
            await self._display(f"\n{attempt.message}\n\n")

        return attempt

    @property
    def attempts(self) -> int:
        """Number of login attempts made."""
        return self._attempt_count

    def reset(self) -> None:
        """Reset attempt counter."""
        self._attempt_count = 0

    def is_locked_out(self) -> bool:
        """Check if user is locked out due to too many attempts."""
        if self._max_attempts == 0:
            return False
        return self._attempt_count >= self._max_attempts
