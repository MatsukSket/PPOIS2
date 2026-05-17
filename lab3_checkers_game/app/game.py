import pygame
from app.consts import cfg, ROWS, COLS
from core.board import Board
from core.enums import Color, PlayerMode


class GameController:
    """Управляет пользовательским вводом и состоянием хода с учетом динамической доски."""

    def __init__(self, board: Board, mode: PlayerMode):
        self.board = board
        self.mode = mode
        self.turn = Color.WHITE
        self.selected = None
        self.valid_moves = {}

    def get_row_col_from_mouse(self, pos: tuple[int, int], flip_board: bool) -> tuple[int, int]:
        """Конвертирует координаты пикселей в логические координаты матрицы доски."""
        x, y = pos
        if y < cfg.BOARD_OFFSET_Y:
            return -1, -1

        x_relative = x - cfg.BOARD_OFFSET_X
        y_relative = y - cfg.BOARD_OFFSET_Y

        if x_relative < 0 or x_relative >= cfg.BOARD_SIZE or y_relative >= cfg.BOARD_SIZE:
            return -1, -1

        v_col = x_relative // cfg.TILE_SIZE
        v_row = y_relative // cfg.TILE_SIZE

        if flip_board:
            return ROWS - 1 - v_row, COLS - 1 - v_col
        return v_row, v_col

    def select(self, row: int, col: int, renderer, flip_board, clock, audio) -> bool:
        """
        Обрабатывает клик по клетке.
        Возвращает True, если состояние изменилось и требуется перерисовка экрана.
        """
        if row == -1 or col == -1:
            return False

        changed = False

        if self.selected:
            if self._try_execute_move(row, col, renderer, flip_board, clock, audio):
                return True

            self.selected = None
            self.valid_moves = {}
            changed = True

        piece = self.board.get_piece(row, col)
        if piece is not None and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return changed

    def _try_execute_move(self, row: int, col: int, renderer, flip_board, clock, audio) -> bool:
        """Проверяет возможность хода и, если он валиден, запускает цепочку действий."""
        target_piece = self.board.get_piece(row, col)

        if target_piece is not None or (row, col) not in self.valid_moves:
            return False

        self._process_move_sequence(row, col, renderer, flip_board, clock, audio)
        self.change_turn()
        return True

    def _process_move_sequence(self, end_row: int, end_col: int, renderer, flip_board, clock, audio):
        """Управляет визуальными эффектами и физическим изменением доски во время хода."""
        start_row, start_col = self.board.get_piece_position(self.selected)
        was_king = self.selected.is_king
        skipped = self.valid_moves[(end_row, end_col)]

        renderer.animate_move(self.selected, (start_row, start_col), (end_row, end_col), self.board, flip_board, clock)

        self.board.move_piece(self.selected, start_row, start_col, end_row, end_col)

        self._handle_captures(skipped, renderer, flip_board, clock, audio)

        if not was_king and self.selected.is_king:
            audio.play_king()

    def _handle_captures(self, skipped: list, renderer, flip_board, clock, audio):
        """Воспроизводит звуки и анимации в зависимости от того, было ли взятие."""
        if skipped:
            audio.play_capture()
            renderer.animate_capture(skipped, self.board, flip_board, clock)
            self.board.remove_piece(skipped)
        else:
            audio.play_move()

    def change_turn(self):
        """Передает ход следующему игроку и сбрасывает текущий выбор."""
        self.valid_moves = {}
        self.selected = None
        self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE