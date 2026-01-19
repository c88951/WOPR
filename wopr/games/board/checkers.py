"""Checkers game for WOPR."""

from typing import Any
import random

from ..base import BaseGame, GameResult


class Checkers(BaseGame):
    """Checkers game against WOPR."""

    NAME = "CHECKERS"
    DESCRIPTION = "Classic game of checkers (draughts)"
    INSTRUCTIONS = """
CHECKERS

You play RED (r/R), WOPR plays BLACK (b/B).
Uppercase letters are kings.

Enter moves as: from-to (e.g., A3-B4)
Jumps are mandatory when available.

Commands: QUIT, BOARD, HELP
"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._board = [[None for _ in range(8)] for _ in range(8)]
        self._init_board()

    def _init_board(self) -> None:
        """Set up initial board position."""
        # Black pieces (WOPR) at top
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self._board[row][col] = "b"

        # Red pieces (player) at bottom
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self._board[row][col] = "r"

    def _render_board(self) -> str:
        """Render the checkers board."""
        lines = []
        lines.append("\n    A   B   C   D   E   F   G   H")
        lines.append("  ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗")

        for row in range(8):
            row_str = f"{8 - row} ║"
            for col in range(8):
                piece = self._board[row][col]
                if piece:
                    # Use circles for pieces
                    if piece == "r":
                        symbol = "○"
                    elif piece == "R":
                        symbol = "◎"
                    elif piece == "b":
                        symbol = "●"
                    elif piece == "B":
                        symbol = "◉"
                    else:
                        symbol = piece
                else:
                    symbol = "·" if (row + col) % 2 == 1 else " "
                row_str += f" {symbol} "
                row_str += "│" if col < 7 else "║"
            lines.append(row_str + f" {8 - row}")
            if row < 7:
                lines.append("  ╟───┼───┼───┼───┼───┼───┼───┼───╢")

        lines.append("  ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝")
        lines.append("    A   B   C   D   E   F   G   H")
        lines.append("\n  RED: ○ (you)  BLACK: ● (WOPR)")
        lines.append("  KINGS: ◎ (you)  ◉ (WOPR)\n")
        return "\n".join(lines)

    def _parse_position(self, pos: str) -> tuple[int, int] | None:
        """Parse position like 'A3' to (row, col)."""
        if len(pos) != 2:
            return None
        col = ord(pos[0].upper()) - ord('A')
        row = 8 - int(pos[1])
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def _get_valid_moves(self, is_red: bool) -> list[tuple[tuple[int, int], tuple[int, int], bool]]:
        """Get all valid moves for a player.

        Returns list of (from, to, is_jump) tuples.
        """
        moves = []
        jumps = []
        pieces = ("r", "R") if is_red else ("b", "B")
        directions = [(-1, -1), (-1, 1)]  # Forward for red
        if not is_red:
            directions = [(1, -1), (1, 1)]  # Forward for black

        for row in range(8):
            for col in range(8):
                piece = self._board[row][col]
                if piece not in pieces:
                    continue

                # Kings can move in all directions
                if piece.isupper():
                    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                else:
                    dirs = directions

                for dr, dc in dirs:
                    new_row, new_col = row + dr, col + dc
                    # Regular move
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if self._board[new_row][new_col] is None:
                            moves.append(((row, col), (new_row, new_col), False))
                        # Jump
                        elif self._board[new_row][new_col] not in pieces and self._board[new_row][new_col] is not None:
                            jump_row, jump_col = new_row + dr, new_col + dc
                            if 0 <= jump_row < 8 and 0 <= jump_col < 8:
                                if self._board[jump_row][jump_col] is None:
                                    jumps.append(((row, col), (jump_row, jump_col), True))

        # Jumps are mandatory
        return jumps if jumps else moves

    def _make_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int], is_jump: bool) -> bool:
        """Execute a move on the board."""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        piece = self._board[from_row][from_col]
        self._board[from_row][from_col] = None
        self._board[to_row][to_col] = piece

        # Remove jumped piece
        if is_jump:
            mid_row = (from_row + to_row) // 2
            mid_col = (from_col + to_col) // 2
            self._board[mid_row][mid_col] = None

        # King promotion
        if piece == "r" and to_row == 0:
            self._board[to_row][to_col] = "R"
        elif piece == "b" and to_row == 7:
            self._board[to_row][to_col] = "B"

        return True

    def _count_pieces(self) -> tuple[int, int]:
        """Count pieces for each side."""
        red = 0
        black = 0
        for row in self._board:
            for piece in row:
                if piece in ("r", "R"):
                    red += 1
                elif piece in ("b", "B"):
                    black += 1
        return red, black

    def _wopr_move(self) -> tuple[tuple[int, int], tuple[int, int]] | None:
        """Calculate WOPR's move."""
        moves = self._get_valid_moves(is_red=False)
        if not moves:
            return None

        # Prefer jumps
        jumps = [m for m in moves if m[2]]
        if jumps:
            from_pos, to_pos, _ = random.choice(jumps)
            return from_pos, to_pos

        # Otherwise random move
        from_pos, to_pos, _ = random.choice(moves)
        return from_pos, to_pos

    async def play(self) -> dict[str, Any]:
        """Play the game."""
        await self.show_instructions()
        self._running = True

        while self._running:
            await self.output(self._render_board())

            red_count, black_count = self._count_pieces()
            await self.output(f"PIECES - RED: {red_count}  BLACK: {black_count}\n")

            if red_count == 0:
                await self.output("WOPR WINS!\n")
                return {"result": GameResult.LOSE}
            if black_count == 0:
                await self.output("YOU WIN!\n")
                return {"result": GameResult.WIN}

            # Player's turn
            valid_moves = self._get_valid_moves(is_red=True)
            if not valid_moves:
                await self.output("NO VALID MOVES. WOPR WINS!\n")
                return {"result": GameResult.LOSE}

            has_jump = any(m[2] for m in valid_moves)
            if has_jump:
                await self.output("JUMP AVAILABLE - YOU MUST JUMP\n")

            await self.output("YOUR MOVE (e.g., A3-B4): ")
            move_str = await self._input()

            cmd = move_str.strip().upper()
            if cmd in {"QUIT", "Q"}:
                return {"result": GameResult.QUIT}
            if cmd == "BOARD":
                continue
            if cmd == "HELP":
                await self.show_instructions()
                continue

            # Parse move
            try:
                parts = cmd.split("-")
                if len(parts) != 2:
                    raise ValueError()
                from_pos = self._parse_position(parts[0])
                to_pos = self._parse_position(parts[1])
                if not from_pos or not to_pos:
                    raise ValueError()
            except:
                await self.output("INVALID FORMAT. USE: A3-B4\n")
                continue

            # Validate move
            is_valid = False
            is_jump = False
            for vfrom, vto, vjump in valid_moves:
                if vfrom == from_pos and vto == to_pos:
                    is_valid = True
                    is_jump = vjump
                    break

            if not is_valid:
                await self.output("ILLEGAL MOVE\n")
                continue

            self._make_move(from_pos, to_pos, is_jump)

            # WOPR's turn
            await self.output("\nWOPR IS THINKING...\n")
            wopr_move = self._wopr_move()
            if wopr_move:
                from_pos, to_pos = wopr_move
                is_jump = abs(from_pos[0] - to_pos[0]) == 2
                self._make_move(from_pos, to_pos, is_jump)
                from_str = chr(ord('A') + from_pos[1]) + str(8 - from_pos[0])
                to_str = chr(ord('A') + to_pos[1]) + str(8 - to_pos[0])
                await self.output(f"WOPR PLAYS: {from_str}-{to_str}\n")
            else:
                await self.output("WOPR CANNOT MOVE. YOU WIN!\n")
                return {"result": GameResult.WIN}

        return {"result": GameResult.QUIT}
