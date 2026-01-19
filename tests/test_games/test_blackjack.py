"""Tests for Blackjack game logic."""

import pytest
from wopr.games.cards.blackjack import Blackjack


class MockIO:
    def __init__(self, inputs: list[str]):
        self.inputs = inputs.copy()
        self.input_index = 0
        self.output = []

    async def output_callback(self, text: str) -> None:
        self.output.append(text)

    async def input_callback(self) -> str:
        if self.input_index < len(self.inputs):
            result = self.inputs[self.input_index]
            self.input_index += 1
            return result
        return "Q"

    def get_output(self) -> str:
        return "".join(self.output)


def test_card_value():
    """Test card value calculation."""
    game = Blackjack(lambda x: None, lambda: "")

    assert game._card_value(("A", "♠")) == 11
    assert game._card_value(("K", "♥")) == 10
    assert game._card_value(("Q", "♦")) == 10
    assert game._card_value(("J", "♣")) == 10
    assert game._card_value(("5", "♠")) == 5
    assert game._card_value(("2", "♥")) == 2


def test_hand_value():
    """Test hand value calculation with ace handling."""
    game = Blackjack(lambda x: None, lambda: "")

    # Simple hand
    hand = [("K", "♠"), ("5", "♥")]
    assert game._hand_value(hand) == 15

    # Blackjack
    hand = [("A", "♠"), ("K", "♥")]
    assert game._hand_value(hand) == 21

    # Ace adjustment (would bust with 11)
    hand = [("A", "♠"), ("8", "♥"), ("5", "♦")]
    assert game._hand_value(hand) == 14  # Ace counts as 1

    # Multiple aces
    hand = [("A", "♠"), ("A", "♥"), ("9", "♦")]
    assert game._hand_value(hand) == 21  # One ace = 11, one = 1


@pytest.mark.asyncio
async def test_blackjack_quit():
    """Test quitting the game."""
    io = MockIO(["Q"])

    game = Blackjack(io.output_callback, io.input_callback)
    result = await game.play()

    from wopr.games.base import GameResult
    assert result["result"] == GameResult.QUIT


@pytest.mark.asyncio
async def test_blackjack_bet_and_stand():
    """Test betting and standing."""
    io = MockIO([
        "10",  # Bet 10
        "S",   # Stand
        "Q",   # Quit after hand
    ])

    game = Blackjack(io.output_callback, io.input_callback)
    result = await game.play()

    output = io.get_output()
    assert "CHIPS" in output
    assert "DEALER" in output


@pytest.mark.asyncio
async def test_blackjack_invalid_bet():
    """Test invalid bet handling."""
    io = MockIO([
        "abc",   # Invalid
        "1000",  # Too high
        "Q",     # Quit
    ])

    game = Blackjack(io.output_callback, io.input_callback)
    result = await game.play()

    output = io.get_output()
    assert "INVALID" in output or "ENTER A NUMBER" in output
