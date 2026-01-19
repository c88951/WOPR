"""Tests for WOPR dialogue system."""

import pytest
from wopr.narrative.dialogue import WOPRDialogue


class MockIO:
    def __init__(self):
        self.output = []

    async def output_callback(self, text: str) -> None:
        self.output.append(text)

    def get_output(self) -> str:
        return "".join(self.output)


def test_game_list():
    """Test that game list contains all games."""
    dialogue = WOPRDialogue()

    expected_games = [
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

    assert dialogue.GAME_LIST == expected_games


def test_parse_game_selection_exact():
    """Test exact game name matching."""
    dialogue = WOPRDialogue()

    assert dialogue.parse_game_selection("CHESS") == "CHESS"
    assert dialogue.parse_game_selection("chess") == "CHESS"
    assert dialogue.parse_game_selection("GLOBAL THERMONUCLEAR WAR") == "GLOBAL THERMONUCLEAR WAR"


def test_parse_game_selection_partial():
    """Test partial game name matching."""
    dialogue = WOPRDialogue()

    assert dialogue.parse_game_selection("GLOBAL") == "GLOBAL THERMONUCLEAR WAR"
    assert dialogue.parse_game_selection("FALKEN") == "FALKEN'S MAZE"


def test_parse_game_selection_number():
    """Test numbered game selection."""
    dialogue = WOPRDialogue()

    assert dialogue.parse_game_selection("1") == "FALKEN'S MAZE"
    assert dialogue.parse_game_selection("7") == "CHESS"
    assert dialogue.parse_game_selection("15") == "GLOBAL THERMONUCLEAR WAR"


def test_parse_game_selection_abbreviations():
    """Test common abbreviations."""
    dialogue = WOPRDialogue()

    assert dialogue.parse_game_selection("GTW") == "GLOBAL THERMONUCLEAR WAR"
    assert dialogue.parse_game_selection("BJ") == "BLACK JACK"
    assert dialogue.parse_game_selection("THERMONUCLEAR") == "GLOBAL THERMONUCLEAR WAR"


def test_parse_game_selection_invalid():
    """Test invalid game selection."""
    dialogue = WOPRDialogue()

    assert dialogue.parse_game_selection("INVALID") is None
    assert dialogue.parse_game_selection("100") is None
    assert dialogue.parse_game_selection("") is None


def test_is_list_request():
    """Test list request detection."""
    dialogue = WOPRDialogue()

    assert dialogue.is_list_request("LIST")
    assert dialogue.is_list_request("list")
    assert dialogue.is_list_request("LIST GAMES")
    assert dialogue.is_list_request("GAMES")

    assert not dialogue.is_list_request("CHESS")
    assert not dialogue.is_list_request("PLAY")
    assert not dialogue.is_list_request("HELP")  # HELP is now separate


def test_is_help_request():
    """Test help request detection."""
    dialogue = WOPRDialogue()

    assert dialogue.is_help_request("HELP")
    assert dialogue.is_help_request("help")
    assert dialogue.is_help_request("?")
    assert dialogue.is_help_request("HINT")
    assert dialogue.is_help_request("COMMANDS")

    assert not dialogue.is_help_request("LIST")
    assert not dialogue.is_help_request("CHESS")


def test_is_quit_request():
    """Test quit request detection."""
    dialogue = WOPRDialogue()

    assert dialogue.is_quit_request("QUIT")
    assert dialogue.is_quit_request("quit")
    assert dialogue.is_quit_request("EXIT")
    assert dialogue.is_quit_request("BYE")
    assert dialogue.is_quit_request("LOGOUT")

    assert not dialogue.is_quit_request("CHESS")
    assert not dialogue.is_quit_request("Q")  # Single letter not quit


@pytest.mark.asyncio
async def test_say_greeting():
    """Test saying a dialogue line."""
    io = MockIO()
    dialogue = WOPRDialogue(output_callback=io.output_callback, typing_speed=0)

    await dialogue.say("greeting")

    output = io.get_output()
    assert "GREETINGS PROFESSOR FALKEN" in output


@pytest.mark.asyncio
async def test_show_game_list():
    """Test showing game list."""
    io = MockIO()
    dialogue = WOPRDialogue(output_callback=io.output_callback, typing_speed=0)

    await dialogue.show_game_list()

    output = io.get_output()
    assert "CHESS" in output
    assert "GLOBAL THERMONUCLEAR WAR" in output
    assert "FALKEN'S MAZE" in output


@pytest.mark.asyncio
async def test_wisdom_sequence():
    """Test wisdom sequence."""
    io = MockIO()
    dialogue = WOPRDialogue(output_callback=io.output_callback, typing_speed=0)

    await dialogue.wisdom_sequence()

    output = io.get_output()
    assert "STRANGE GAME" in output
    assert "WINNING MOVE" in output
    assert "NOT TO PLAY" in output
    assert "CHESS" in output
