"""Tests for Tic-Tac-Toe game logic."""

import pytest
from wopr.games.board.tictactoe import TicTacToe, TicTacToeLearning


class MockIO:
    """Mock input/output for testing games."""

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
        return "Q"  # Default to quit

    def get_output(self) -> str:
        return "".join(self.output)


@pytest.mark.asyncio
async def test_tictactoe_player_wins():
    """Test that player can win."""
    # This sequence should let player win with X in first column
    # WOPR plays optimally, so we need to set up a specific scenario
    io = MockIO([
        "1,1",  # Player X top-left
        "2,1",  # Player X middle-left
        "3,1",  # Player X bottom-left - wins!
    ])

    game = TicTacToe(io.output_callback, io.input_callback)
    # Manually set up a board state where player can win
    game._board = [
        ["X", "O", " "],
        ["X", "O", " "],
        [" ", " ", " "],
    ]

    # Player plays 3,1 to win
    io.inputs = ["3,1"]
    io.input_index = 0

    result = await game.play()
    output = io.get_output()

    assert "YOU WIN" in output


@pytest.mark.asyncio
async def test_tictactoe_quit():
    """Test quitting the game."""
    io = MockIO(["Q"])

    game = TicTacToe(io.output_callback, io.input_callback)
    result = await game.play()

    from wopr.games.base import GameResult
    assert result["result"] == GameResult.QUIT


@pytest.mark.asyncio
async def test_tictactoe_invalid_move():
    """Test invalid move handling."""
    io = MockIO([
        "invalid",  # Invalid format
        "5,5",      # Out of bounds
        "Q",        # Quit
    ])

    game = TicTacToe(io.output_callback, io.input_callback)
    result = await game.play()

    output = io.get_output()
    assert "INVALID" in output


@pytest.mark.asyncio
async def test_tictactoe_check_winner():
    """Test winner detection."""
    game = TicTacToe(lambda x: None, lambda: "")

    # Test row win
    game._board = [
        ["X", "X", "X"],
        [" ", " ", " "],
        [" ", " ", " "],
    ]
    assert game._check_winner() == "X"

    # Test column win
    game._board = [
        ["O", " ", " "],
        ["O", " ", " "],
        ["O", " ", " "],
    ]
    assert game._check_winner() == "O"

    # Test diagonal win
    game._board = [
        ["X", " ", " "],
        [" ", "X", " "],
        [" ", " ", "X"],
    ]
    assert game._check_winner() == "X"

    # Test draw
    game._board = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"],
    ]
    assert game._check_winner() == "DRAW"

    # Test no winner yet
    game._board = [
        ["X", " ", " "],
        [" ", " ", " "],
        [" ", " ", " "],
    ]
    assert game._check_winner() is None


@pytest.mark.asyncio
async def test_tictactoe_minimax_optimal():
    """Test that WOPR plays optimally."""
    game = TicTacToe(lambda x: None, lambda: "")

    # If WOPR can win, it should
    game._board = [
        ["O", "O", " "],
        ["X", "X", " "],
        [" ", " ", " "],
    ]
    move = game._computer_move()
    assert move == (0, 2)  # Complete the winning row


@pytest.mark.asyncio
async def test_learning_demonstration():
    """Test the learning sequence runs."""
    output = []

    async def capture(text: str):
        output.append(text)

    learning = TicTacToeLearning(capture)
    await learning.run_demonstration()

    full_output = "".join(output)
    assert "ANALYZING" in full_output
    assert "GAMES ANALYZED" in full_output
    assert "WINNER: NONE" in full_output or "POSSIBLE WINNER: NONE" in full_output
