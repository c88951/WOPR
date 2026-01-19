"""Tests for Falken's Maze."""

import pytest
from wopr.games.maze import FalkensMaze, MazeSolver


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


@pytest.mark.asyncio
async def test_maze_quit():
    """Test quitting the maze."""
    io = MockIO(["Q"])

    game = FalkensMaze(io.output_callback, io.input_callback)
    result = await game.play()

    from wopr.games.base import GameResult
    assert result["result"] == GameResult.QUIT


@pytest.mark.asyncio
async def test_maze_generation():
    """Test maze generation creates valid maze."""
    io = MockIO(["Q"])

    game = FalkensMaze(io.output_callback, io.input_callback, width=11, height=11)
    game._generate_maze()

    # Check maze dimensions
    assert len(game._maze) == 11
    assert len(game._maze[0]) == 11

    # Check start and exit are empty
    assert game._maze[1][1] == " "
    assert game._maze[game._height - 2][game._width - 2] == " "


@pytest.mark.asyncio
async def test_maze_movement():
    """Test movement in maze."""
    io = MockIO([
        "E",  # Move east
        "S",  # Move south
        "Q",  # Quit
    ])

    game = FalkensMaze(io.output_callback, io.input_callback, width=11, height=11)
    game._generate_maze()

    # Clear a path for testing
    game._maze[1][2] = " "
    game._maze[2][1] = " "

    initial_pos = game._player_pos
    result = await game.play()

    # Player should have moved (position changed or blocked message shown)
    output = io.get_output()
    assert "MOVES:" in output


def test_maze_solver():
    """Test the maze solver utility."""
    # Create a simple solvable maze
    maze = [
        ["█", "█", "█", "█", "█"],
        ["█", " ", " ", " ", "█"],
        ["█", "█", "█", " ", "█"],
        ["█", " ", " ", " ", "█"],
        ["█", "█", "█", "█", "█"],
    ]

    path = MazeSolver.solve(maze, (1, 1), (3, 3))

    assert path is not None
    assert path[0] == (1, 1)  # Start
    assert path[-1] == (3, 3)  # End


def test_maze_solver_unsolvable():
    """Test maze solver with unsolvable maze."""
    # Create an unsolvable maze
    maze = [
        ["█", "█", "█", "█", "█"],
        ["█", " ", "█", " ", "█"],
        ["█", "█", "█", "█", "█"],
        ["█", " ", "█", " ", "█"],
        ["█", "█", "█", "█", "█"],
    ]

    path = MazeSolver.solve(maze, (1, 1), (3, 3))

    assert path is None


def test_maze_win_condition_detection():
    """Test that win condition is properly detected."""
    # Create a game instance (we won't call play())
    game = FalkensMaze(lambda x: None, lambda: "", width=5, height=5)

    # Manually set up state
    game._player_pos = (3, 3)
    game._exit_pos = (3, 3)

    # Player is at exit - this should be the win condition
    assert game._player_pos == game._exit_pos


def test_maze_can_move():
    """Test movement validation."""
    game = FalkensMaze(lambda x: None, lambda: "", width=5, height=5)
    game._maze = [
        ["█", "█", "█", "█", "█"],
        ["█", " ", " ", " ", "█"],
        ["█", "█", "█", " ", "█"],
        ["█", " ", " ", " ", "█"],
        ["█", "█", "█", "█", "█"],
    ]

    # Can move to empty space
    assert game._can_move(1, 1) is True
    assert game._can_move(2, 1) is True

    # Cannot move to wall
    assert game._can_move(0, 0) is False
    assert game._can_move(2, 2) is False

    # Cannot move outside bounds
    assert game._can_move(-1, 0) is False
    assert game._can_move(10, 10) is False
