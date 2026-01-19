"""Tic-Tac-Toe game - critical for WOPR's learning sequence."""

from typing import Callable, Awaitable, Any
import asyncio
import random

from ..base import BaseGame, GameResult


class TicTacToe(BaseGame):
    """Tic-Tac-Toe game."""

    NAME = "TIC-TAC-TOE"
    DESCRIPTION = "The classic game of X's and O's"
    INSTRUCTIONS = """
TIC-TAC-TOE

Place your mark (X) by entering coordinates (1-3, 1-3).
Example: 1,1 for top-left, 2,2 for center

Win by getting three in a row horizontally, vertically, or diagonally.
"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._board = [[" " for _ in range(3)] for _ in range(3)]
        self._player = "X"
        self._computer = "O"

    def _render_board(self) -> str:
        """Render the tic-tac-toe board with larger cells."""
        lines = []
        lines.append("")
        lines.append("          1         2         3")
        lines.append("     ┌─────────┬─────────┬─────────┐")
        for i, row in enumerate(self._board):
            # Top padding
            lines.append("     │         │         │         │")
            # Middle row with X or O
            lines.append(f"  {i + 1}  │    {row[0]}    │    {row[1]}    │    {row[2]}    │")
            # Bottom padding
            lines.append("     │         │         │         │")
            if i < 2:
                lines.append("     ├─────────┼─────────┼─────────┤")
        lines.append("     └─────────┴─────────┴─────────┘")
        lines.append("")
        return "\n".join(lines)

    def _check_winner(self) -> str | None:
        """Check if there's a winner. Returns 'X', 'O', 'DRAW', or None."""
        # Check rows
        for row in self._board:
            if row[0] == row[1] == row[2] != " ":
                return row[0]

        # Check columns
        for col in range(3):
            if self._board[0][col] == self._board[1][col] == self._board[2][col] != " ":
                return self._board[0][col]

        # Check diagonals
        if self._board[0][0] == self._board[1][1] == self._board[2][2] != " ":
            return self._board[0][0]
        if self._board[0][2] == self._board[1][1] == self._board[2][0] != " ":
            return self._board[0][2]

        # Check for draw
        if all(self._board[r][c] != " " for r in range(3) for c in range(3)):
            return "DRAW"

        return None

    def _get_empty_cells(self) -> list[tuple[int, int]]:
        """Get list of empty cells."""
        return [
            (r, c)
            for r in range(3)
            for c in range(3)
            if self._board[r][c] == " "
        ]

    def _minimax(self, is_maximizing: bool, depth: int = 0) -> tuple[int, tuple[int, int] | None]:
        """Minimax algorithm for optimal play."""
        winner = self._check_winner()
        if winner == self._computer:
            return 10 - depth, None
        if winner == self._player:
            return depth - 10, None
        if winner == "DRAW":
            return 0, None

        empty = self._get_empty_cells()
        if not empty:
            return 0, None

        best_move = None
        if is_maximizing:
            best_score = -100
            for r, c in empty:
                self._board[r][c] = self._computer
                score, _ = self._minimax(False, depth + 1)
                self._board[r][c] = " "
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
        else:
            best_score = 100
            for r, c in empty:
                self._board[r][c] = self._player
                score, _ = self._minimax(True, depth + 1)
                self._board[r][c] = " "
                if score < best_score:
                    best_score = score
                    best_move = (r, c)

        return best_score, best_move

    def _computer_move(self) -> tuple[int, int]:
        """Make the optimal computer move."""
        _, move = self._minimax(True)
        if move:
            return move
        # Fallback to random if something goes wrong
        empty = self._get_empty_cells()
        return random.choice(empty) if empty else (0, 0)

    async def play(self) -> dict[str, Any]:
        """Play the game."""
        await self.show_instructions()
        self._running = True

        while self._running:
            # Show board
            await self.output(self._render_board() + "\n")

            # Check for game end
            winner = self._check_winner()
            if winner:
                if winner == "DRAW":
                    await self.output("\nDRAW - NO WINNER\n")
                    return {"result": GameResult.DRAW}
                elif winner == self._player:
                    await self.output("\nYOU WIN\n")
                    return {"result": GameResult.WIN}
                else:
                    await self.output("\nWOPR WINS\n")
                    return {"result": GameResult.LOSE}

            # Player move
            await self.output("\nYOUR MOVE (row,col or Q to quit): ")
            move_str = await self._input()

            if move_str.upper() in {"Q", "QUIT"}:
                return {"result": GameResult.QUIT}

            try:
                parts = move_str.replace(" ", ",").split(",")
                row, col = int(parts[0]) - 1, int(parts[1]) - 1
                if not (0 <= row < 3 and 0 <= col < 3):
                    await self.output("INVALID POSITION\n")
                    continue
                if self._board[row][col] != " ":
                    await self.output("POSITION OCCUPIED\n")
                    continue
            except (ValueError, IndexError):
                await self.output("INVALID INPUT - USE FORMAT: row,col\n")
                continue

            self._board[row][col] = self._player

            # Check if player won
            if self._check_winner():
                continue

            # Computer move
            comp_r, comp_c = self._computer_move()
            self._board[comp_r][comp_c] = self._computer
            await self.output(f"\nWOPR PLAYS: {comp_r + 1},{comp_c + 1}\n")

        return {"result": GameResult.QUIT}


class TicTacToeLearning:
    """Demonstrates WOPR learning that tic-tac-toe is unwinnable."""

    def __init__(self, output_callback: Callable[[str], Awaitable[None]]) -> None:
        self._output = output_callback

    def _render_mini_board(self, board: list[str]) -> str:
        """Render a compact 3x3 board for rapid display."""
        return (
            f" {board[0]} | {board[1]} | {board[2]} \n"
            f"---+---+---\n"
            f" {board[3]} | {board[4]} | {board[5]} \n"
            f"---+---+---\n"
            f" {board[6]} | {board[7]} | {board[8]} \n"
        )

    async def run_demonstration(self) -> None:
        """Run the rapid tic-tac-toe learning demonstration."""
        await self._output("\nANALYZING TIC-TAC-TOE...\n")
        await self._output("=" * 50 + "\n\n")
        await asyncio.sleep(0.5)

        # Show a few sample games with outcomes
        sample_games = [
            # Game 1: X wins (but this is suboptimal play)
            (["X", "O", "X", "O", "X", " ", "X", " ", "O"], "X WINS"),
            # Game 2: O wins
            (["X", "X", "O", " ", "O", "X", "O", " ", " "], "O WINS"),
            # Game 3: Draw (optimal play)
            (["X", "O", "X", "X", "O", "O", "O", "X", "X"], "DRAW"),
            # Game 4: Draw
            (["O", "X", "O", "X", "X", "O", "X", "O", "X"], "DRAW"),
            # Game 5: Draw
            (["X", "O", "X", "O", "O", "X", "X", "X", "O"], "DRAW"),
        ]

        await self._output("SAMPLE GAMES:\n\n")

        for i, (board, result) in enumerate(sample_games):
            await self._output(f"Game {i + 1}:        Result: {result}\n")
            await self._output(self._render_mini_board(board))
            await self._output("\n")
            await asyncio.sleep(0.3)

        # Rapid analysis counter
        await self._output("ANALYZING ALL POSSIBLE GAMES...\n\n")
        game_counts = [1000, 5000, 25000, 100000, 200000, 255168]

        for count in game_counts:
            await self._output(f"  Games analyzed: {count:,}...\n")
            await asyncio.sleep(0.15)

        await self._output("\n" + "=" * 50 + "\n")
        await self._output("ANALYSIS COMPLETE\n")
        await self._output("=" * 50 + "\n\n")
        await asyncio.sleep(0.3)
        await self._output("TOTAL GAMES ANALYZED: 255,168\n")
        await asyncio.sleep(0.3)
        await self._output("OPTIMAL PLAY RESULTS IN: DRAW\n")
        await asyncio.sleep(0.3)
        await self._output("POSSIBLE WINNER WITH OPTIMAL PLAY: NONE\n\n")
        await asyncio.sleep(1.0)
