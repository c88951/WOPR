"""Chess game for WOPR using python-chess."""

from typing import Any
import asyncio

from ..base import BaseGame, GameResult

try:
    import chess
    import chess.engine
    CHESS_AVAILABLE = True
except ImportError:
    CHESS_AVAILABLE = False


class ChessGame(BaseGame):
    """Chess game against WOPR."""

    NAME = "CHESS"
    DESCRIPTION = "The classic game of strategy"
    INSTRUCTIONS = """
CHESS

Enter moves in algebraic notation:
  e2e4  - Move piece from e2 to e4
  e7e8q - Pawn promotion (add piece letter)
  O-O   - Kingside castle
  O-O-O - Queenside castle

Commands: QUIT, RESIGN, BOARD, HELP
"""

    # Unicode chess pieces
    PIECES = {
        "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
        "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",
    }

    # ASCII pieces for compatibility
    ASCII_PIECES = {
        "K": "K", "Q": "Q", "R": "R", "B": "B", "N": "N", "P": "P",
        "k": "k", "q": "q", "r": "r", "b": "b", "n": "n", "p": "p",
    }

    def __init__(
        self,
        output_callback,
        input_callback,
        difficulty: int = 3,
        **kwargs
    ) -> None:
        super().__init__(output_callback, input_callback, **kwargs)
        self._difficulty = max(1, min(5, difficulty))
        self._board = None
        self._use_unicode = True

    def _render_board(self) -> str:
        """Render the chess board as ASCII."""
        if not self._board:
            return ""

        pieces = self.PIECES if self._use_unicode else self.ASCII_PIECES
        lines = []
        lines.append("\n    a   b   c   d   e   f   g   h")
        lines.append("  ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗")

        for rank in range(7, -1, -1):
            row = f"{rank + 1} ║"
            for file in range(8):
                square = chess.square(file, rank)
                piece = self._board.piece_at(square)
                if piece:
                    symbol = pieces.get(piece.symbol(), piece.symbol())
                else:
                    # Checkerboard pattern
                    symbol = "·" if (rank + file) % 2 == 0 else " "
                row += f" {symbol} "
                row += "│" if file < 7 else "║"
            lines.append(row + f" {rank + 1}")
            if rank > 0:
                lines.append("  ╟───┼───┼───┼───┼───┼───┼───┼───╢")

        lines.append("  ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝")
        lines.append("    a   b   c   d   e   f   g   h\n")
        return "\n".join(lines)

    def _get_wopr_move(self) -> chess.Move | None:
        """Calculate WOPR's move using simple evaluation."""
        if not self._board:
            return None

        # Piece values for basic evaluation
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }

        def evaluate_board(board: chess.Board) -> int:
            """Simple board evaluation."""
            if board.is_checkmate():
                return -99999 if board.turn else 99999
            if board.is_stalemate() or board.is_insufficient_material():
                return 0

            score = 0
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece:
                    value = piece_values.get(piece.piece_type, 0)
                    if piece.color == chess.WHITE:
                        score -= value  # WOPR plays black
                    else:
                        score += value
            return score

        def minimax(board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
            """Minimax with alpha-beta pruning."""
            if depth == 0 or board.is_game_over():
                return evaluate_board(board)

            if maximizing:
                max_eval = -999999
                for move in board.legal_moves:
                    board.push(move)
                    eval_score = minimax(board, depth - 1, alpha, beta, False)
                    board.pop()
                    max_eval = max(max_eval, eval_score)
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
                return max_eval
            else:
                min_eval = 999999
                for move in board.legal_moves:
                    board.push(move)
                    eval_score = minimax(board, depth - 1, alpha, beta, True)
                    board.pop()
                    min_eval = min(min_eval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
                return min_eval

        # Search depth based on difficulty
        depth = self._difficulty + 1

        best_move = None
        best_score = -999999

        for move in self._board.legal_moves:
            self._board.push(move)
            score = minimax(self._board, depth, -999999, 999999, False)
            self._board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    async def play(self) -> dict[str, Any]:
        """Play the game."""
        if not CHESS_AVAILABLE:
            await self.output("\nCHESS MODULE NOT AVAILABLE\n")
            await self.output("Install with: pip install python-chess\n")
            return {"result": GameResult.QUIT}

        await self.show_instructions()
        self._board = chess.Board()
        self._running = True

        await self.output("YOU PLAY WHITE. WOPR PLAYS BLACK.\n")
        await self.output(f"DIFFICULTY LEVEL: {self._difficulty}\n\n")

        while self._running and not self._board.is_game_over():
            # Show board
            await self.output(self._render_board())

            # Check status
            if self._board.is_check():
                await self.output("CHECK!\n")

            # Player's turn (White)
            if self._board.turn == chess.WHITE:
                await self.output("YOUR MOVE: ")
                move_str = await self._input()

                cmd = move_str.strip().upper()
                if cmd in {"QUIT", "Q"}:
                    return {"result": GameResult.QUIT}
                if cmd == "RESIGN":
                    await self.output("\nYOU RESIGN. WOPR WINS.\n")
                    return {"result": GameResult.LOSE}
                if cmd == "BOARD":
                    continue
                if cmd == "HELP":
                    await self.show_instructions()
                    continue

                # Try to parse move
                try:
                    # Handle castling
                    if cmd in {"O-O", "0-0"}:
                        move = self._board.parse_san("O-O")
                    elif cmd in {"O-O-O", "0-0-0"}:
                        move = self._board.parse_san("O-O-O")
                    else:
                        # Try UCI notation first, then SAN
                        try:
                            move = chess.Move.from_uci(move_str.lower())
                            if move not in self._board.legal_moves:
                                raise ValueError()
                        except:
                            move = self._board.parse_san(move_str)

                    self._board.push(move)
                except Exception:
                    await self.output("ILLEGAL MOVE\n")
                    continue

            # WOPR's turn (Black)
            else:
                await self.output("WOPR IS THINKING...\n")
                await asyncio.sleep(0.5)

                move = self._get_wopr_move()
                if move:
                    self._board.push(move)
                    await self.output(f"WOPR PLAYS: {move.uci()}\n")
                else:
                    await self.output("WOPR CANNOT MOVE\n")
                    break

        # Game over
        await self.output(self._render_board())

        if self._board.is_checkmate():
            if self._board.turn == chess.WHITE:
                await self.output("CHECKMATE! WOPR WINS.\n")
                return {"result": GameResult.LOSE}
            else:
                await self.output("CHECKMATE! YOU WIN.\n")
                return {"result": GameResult.WIN}
        elif self._board.is_stalemate():
            await self.output("STALEMATE - DRAW\n")
            return {"result": GameResult.DRAW}
        elif self._board.is_insufficient_material():
            await self.output("INSUFFICIENT MATERIAL - DRAW\n")
            return {"result": GameResult.DRAW}
        else:
            await self.output("GAME OVER - DRAW\n")
            return {"result": GameResult.DRAW}
