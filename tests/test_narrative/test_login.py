"""Tests for login handler."""

import pytest
from wopr.narrative.login import LoginHandler, LoginResult


class MockIO:
    def __init__(self):
        self.output = []

    async def output_callback(self, text: str) -> None:
        self.output.append(text)

    def get_output(self) -> str:
        return "".join(self.output)


def test_backdoor_login():
    """Test that 'joshua' grants access."""
    handler = LoginHandler()

    attempt = handler.validate("joshua")
    assert attempt.result == LoginResult.BACKDOOR
    assert "GREETINGS" in attempt.message


def test_backdoor_login_case_insensitive():
    """Test that 'Joshua' and 'JOSHUA' work."""
    handler = LoginHandler()

    attempt = handler.validate("Joshua")
    assert attempt.result == LoginResult.BACKDOOR

    attempt = handler.validate("JOSHUA")
    assert attempt.result == LoginResult.BACKDOOR


def test_invalid_login():
    """Test that invalid usernames are rejected."""
    handler = LoginHandler()

    attempt = handler.validate("admin")
    assert attempt.result == LoginResult.INVALID
    assert "NOT RECOGNIZED" in attempt.message

    attempt = handler.validate("")
    assert attempt.result == LoginResult.INVALID

    attempt = handler.validate("falken")
    assert attempt.result == LoginResult.INVALID


def test_help_at_login():
    """Test that help is available at login."""
    handler = LoginHandler()

    attempt = handler.validate("help")
    assert attempt.result == LoginResult.HELP
    assert "FALKEN" in attempt.message or "DOCUMENTATION" in attempt.message

    # Help with different cases
    attempt = handler.validate("HELP")
    assert attempt.result == LoginResult.HELP

    attempt = handler.validate("?")
    assert attempt.result == LoginResult.HELP

    attempt = handler.validate("hint")
    assert attempt.result == LoginResult.HELP


def test_help_doesnt_count_as_attempt():
    """Test that help requests don't count as login attempts."""
    handler = LoginHandler()

    handler.validate("help")
    assert handler.attempts == 0

    handler.validate("wrong")
    assert handler.attempts == 1

    handler.validate("HELP")
    assert handler.attempts == 1  # Still 1


def test_attempt_counter():
    """Test that attempts are counted."""
    handler = LoginHandler()

    assert handler.attempts == 0

    handler.validate("wrong")
    assert handler.attempts == 1

    handler.validate("wrong")
    assert handler.attempts == 2

    handler.validate("joshua")
    assert handler.attempts == 3


def test_reset():
    """Test resetting the handler."""
    handler = LoginHandler()

    handler.validate("test")
    handler.validate("test")
    assert handler.attempts == 2

    handler.reset()
    assert handler.attempts == 0


@pytest.mark.asyncio
async def test_login_with_output():
    """Test login with output callback."""
    io = MockIO()
    handler = LoginHandler(output_callback=io.output_callback)

    await handler.attempt_login("joshua")

    output = io.get_output()
    assert "GREETINGS" in output


@pytest.mark.asyncio
async def test_invalid_login_with_output():
    """Test invalid login output."""
    io = MockIO()
    handler = LoginHandler(output_callback=io.output_callback)

    await handler.attempt_login("hacker")

    output = io.get_output()
    assert "NOT RECOGNIZED" in output
