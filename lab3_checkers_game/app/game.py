import pygame
from app.consts import TILE_SIZE, ROWS, COLS, UI_HEIGHT
from core.board import Board
from core.enums import Color, PlayerMode


class GameController:
    """Управляет пользовательским вводом, выбором шашек и сменой ходов."""

    def __init__(self, board: Board, mode: PlayerMode):
        self.board = board
        self.mode = mode
        self.turn = Color.WHITE  # Белые всегда ходят первыми
        self.selected = None
        self.valid_moves = {}

    def get_row_col_from_mouse(self, pos: tuple[int, int], flip_board: bool) -> tuple[int, int]:
        """Переводит пиксели экрана в индексы матрицы с учетом верхней панели."""
        x, y = pos

        if y < UI_HEIGHT:
            return -1, -1

        v_col = x // TILE_SIZE
        v_row = (y - UI_HEIGHT) // TILE_SIZE

        if flip_board:
            return ROWS - 1 - v_row, COLS - 1 - v_col
        return v_row, v_col

    def select(self, row: int, col: int, renderer, flip_board, clock, audio) -> bool:
        """
            Обрабатывает клик по клетке доски.
            Пытается выбрать шашку или совершить ход ранее выбранной шашкой.
        """
        if self.selected:
            result = self._move(row, col, renderer, flip_board, clock, audio)
            if not result:
                self.selected = None
                self.valid_moves = {}
                self.select(row, col, renderer, flip_board, clock, audio)

        piece = self.board.get_piece(row, col)
        if piece is not None and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row: int, col: int, renderer, flip_board, clock, audio) -> bool:
        """Совершает ход, проигрывает анимацию и звуки."""
        piece = self.board.get_piece(row, col)

        if self.selected and piece is None and (row, col) in self.valid_moves:
            start_row, start_col = self.board.get_piece_position(self.selected)
            was_king = self.selected.is_king

            renderer.animate_move(
                self.selected, (start_row, start_col), (row, col),
                self.board, flip_board, clock
            )

            self.board.move_piece(self.selected, start_row, start_col, row, col)
            skipped = self.valid_moves[(row, col)]

            if skipped:
                self.board.remove_piece(skipped)
                audio.play_capture()
            else:
                audio.play_move()

            if not was_king and self.selected.is_king:
                audio.play_king()

            self.change_turn()
            return True

        return False


    def change_turn(self):
        """Передает ход следующему игроку и сбрасывает текущий выбор."""
        self.valid_moves = {}
        self.selected = None
        self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE