"""Tests for Chess game logic."""

import pytest

# Check if python-chess is available
try:
    import chess
    CHESS_AVAILABLE = True
except ImportError:
    CHESS_AVAILABLE = False

from wopr.games.board.chess import ChessGame


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
        return "QUIT"

    def get_output(self) -> str:
        return "".join(self.output)


@pytest.mark.skipif(not CHESS_AVAILABLE, reason="python-chess not installed")
@pytest.mark.asyncio
async def test_chess_quit():
    """Test quitting chess."""
    io = MockIO(["QUIT"])

    game = ChessGame(io.output_callback, io.input_callback)
    result = await game.play()

    from wopr.games.base import GameResult
    assert result["result"] == GameResult.QUIT


@pytest.mark.skipif(not CHESS_AVAILABLE, reason="python-chess not installed")
@pytest.mark.asyncio
async def test_chess_invalid_move():
    """Test invalid move handling."""
    io = MockIO([
        "invalid",  # Invalid move
        "a2a5",     # Illegal pawn move
        "QUIT",
    ])

    game = ChessGame(io.output_callback, io.input_callback)
    result = await game.play()

    output = io.get_output()
    assert "ILLEGAL" in output


@pytest.mark.skipif(not CHESS_AVAILABLE, reason="python-chess not installed")
@pytest.mark.asyncio
async def test_chess_valid_move():
    """Test valid move."""
    io = MockIO([
        "e2e4",  # Valid pawn move
        "QUIT",
    ])

    game = ChessGame(io.output_callback, io.input_callback)
    result = await game.play()

    output = io.get_output()
    assert "WOPR PLAYS" in output  # WOPR responded


@pytest.mark.skipif(not CHESS_AVAILABLE, reason="python-chess not installed")
@pytest.mark.asyncio
async def test_chess_resign():
    """Test resignation."""
    io = MockIO(["RESIGN"])

    game = ChessGame(io.output_callback, io.input_callback)
    result = await game.play()

    output = io.get_output()
    assert "RESIGN" in output
    from wopr.games.base import GameResult
    assert result["result"] == GameResult.LOSE


@pytest.mark.skipif(not CHESS_AVAILABLE, reason="python-chess not installed")
def test_chess_board_rendering():
    """Test board rendering."""
    game = ChessGame(lambda x: None, lambda: "")
    game._board = chess.Board()

    board_str = game._render_board()

    # Check for board elements
    assert "a" in board_str and "h" in board_str  # Column labels
    assert "1" in board_str and "8" in board_str  # Row labels
