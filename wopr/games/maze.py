"""Falken's Maze - procedurally generated maze game."""

from typing import Any
import random

from .base import BaseGame, GameResult


class FalkensMaze(BaseGame):
    """Falken's Maze - navigate through a procedurally generated maze."""

    NAME = "FALKEN'S MAZE"
    DESCRIPTION = "Find your way through the labyrinth"
    INSTRUCTIONS = """
FALKEN'S MAZE

Navigate from START (S) to EXIT (E).
You are represented by @.

Commands:
  N or W - Move North (up)
  S or X - Move South (down)
  E or D - Move East (right)
  W or A - Move West (left)
  Q      - Quit

Walls are represented by █
"""

    def __init__(
        self,
        output_callback,
        input_callback,
        width: int = 21,
        height: int = 15,
        **kwargs
    ) -> None:
        super().__init__(output_callback, input_callback, **kwargs)
        self._width = width if width % 2 == 1 else width + 1
        self._height = height if height % 2 == 1 else height + 1
        self._maze = []
        self._player_pos = (1, 1)
        self._exit_pos = (0, 0)
        self._moves = 0

    def _generate_maze(self) -> None:
        """Generate a maze using recursive backtracking."""
        # Initialize with all walls
        self._maze = [["█" for _ in range(self._width)] for _ in range(self._height)]

        # Carve passages using recursive backtracking
        def carve(x: int, y: int) -> None:
            self._maze[y][x] = " "
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < self._width - 1 and 0 < ny < self._height - 1:
                    if self._maze[ny][nx] == "█":
                        # Carve through the wall between
                        self._maze[y + dy // 2][x + dx // 2] = " "
                        carve(nx, ny)

        # Start from a random odd position
        start_x = random.randrange(1, self._width - 1, 2)
        start_y = random.randrange(1, self._height - 1, 2)
        carve(start_x, start_y)

        # Set player start position (top-left area)
        self._player_pos = (1, 1)
        self._maze[1][1] = " "

        # Set exit position (bottom-right area)
        self._exit_pos = (self._width - 2, self._height - 2)
        self._maze[self._height - 2][self._width - 2] = " "

        # Ensure there's a path - connect if needed
        # Make sure start and end are accessible
        if self._maze[1][2] == "█" and self._maze[2][1] == "█":
            self._maze[1][2] = " "
        if self._maze[self._height - 2][self._width - 3] == "█" and self._maze[self._height - 3][self._width - 2] == "█":
            self._maze[self._height - 2][self._width - 3] = " "

    def _render_maze(self) -> str:
        """Render the maze with player and exit."""
        lines = []
        lines.append("╔" + "═" * self._width + "╗")

        for y in range(self._height):
            row = "║"
            for x in range(self._width):
                if (x, y) == self._player_pos:
                    row += "@"
                elif (x, y) == self._exit_pos:
                    row += "E"
                elif x == 1 and y == 1:
                    row += "S"
                else:
                    row += self._maze[y][x]
            row += "║"
            lines.append(row)

        lines.append("╚" + "═" * self._width + "╝")
        lines.append(f"\nMOVES: {self._moves}    S=START  E=EXIT  @=YOU")
        return "\n".join(lines)

    def _can_move(self, x: int, y: int) -> bool:
        """Check if a position is valid to move to."""
        if 0 <= x < self._width and 0 <= y < self._height:
            return self._maze[y][x] != "█"
        return False

    async def play(self) -> dict[str, Any]:
        """Play the game."""
        await self.show_instructions()

        # Generate maze
        await self.output("GENERATING MAZE...\n")
        self._generate_maze()
        self._running = True

        while self._running:
            await self.output("\n" + self._render_maze() + "\n")

            # Check win condition
            if self._player_pos == self._exit_pos:
                await self.output(f"\n*** MAZE COMPLETED IN {self._moves} MOVES ***\n")
                return {"result": GameResult.WIN, "moves": self._moves}

            await self.output("\nMOVE (N/S/E/W or Q): ")
            cmd = (await self._input()).strip().upper()

            if cmd in {"Q", "QUIT"}:
                return {"result": GameResult.QUIT}

            # Parse direction
            dx, dy = 0, 0
            if cmd in {"N", "UP", "W"}:  # North
                dy = -1
            elif cmd in {"S", "DOWN", "X"}:  # South
                dy = 1
            elif cmd in {"E", "RIGHT", "D"}:  # East
                dx = 1
            elif cmd in {"W", "LEFT", "A"}:  # West
                dx = -1
            else:
                await self.output("INVALID COMMAND\n")
                continue

            # Try to move
            new_x = self._player_pos[0] + dx
            new_y = self._player_pos[1] + dy

            if self._can_move(new_x, new_y):
                self._player_pos = (new_x, new_y)
                self._moves += 1
            else:
                await self.output("BLOCKED!\n")

        return {"result": GameResult.QUIT}


class MazeSolver:
    """Utility to solve mazes (for validation)."""

    @staticmethod
    def solve(maze: list[list[str]], start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]] | None:
        """Solve a maze using BFS. Returns path or None if unsolvable."""
        from collections import deque

        height = len(maze)
        width = len(maze[0])
        visited = set()
        queue = deque([(start, [start])])

        while queue:
            (x, y), path = queue.popleft()

            if (x, y) == end:
                return path

            if (x, y) in visited:
                continue
            visited.add((x, y))

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if maze[ny][nx] != "█" and (nx, ny) not in visited:
                        queue.append(((nx, ny), path + [(nx, ny)]))

        return None
