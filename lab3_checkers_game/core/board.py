from typing import Optional, List
from core.enums import Color
from core.piece import Piece
from app.consts import ROWS, COLS



class Board:
    """Представление доски."""

    def __init__(self):
        self.grid: List[List[Optional[Piece]]] = []
        self.white_left = self.black_left = 12
        self.white_kings = self.black_kings = 0
        self._create_starting_grid()

    def _create_starting_grid(self) -> None:
        """Определяет начальную расстановку шашек на черных клетках."""
        for row in range(ROWS):
            self.grid.append([])
            for col in range(COLS):
                if (row + col) % 2 != 0:
                    if row < 3:
                        self.grid[row].append(Piece(Color.BLACK))
                    elif row > 4:
                        self.grid[row].append(Piece(Color.WHITE))
                    else:
                        self.grid[row].append(None)
                else:
                    self.grid[row].append(None)

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Возвращает объект шашки на заданной позиции или None."""
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.grid[row][col]
        return None

    def move_piece(self, piece: Piece, start_row: int, start_col: int, end_row: int, end_col: int) -> None:
        """Перемещает шашку в матрице."""
        self.grid[start_row][start_col], self.grid[end_row][end_col] = self.grid[end_row][end_col], self.grid[start_row][start_col]

        if piece.color == Color.WHITE and end_row == 0 and not piece.is_king:
            piece.make_king()
            self.white_kings += 1
        elif piece.color == Color.BLACK and end_row == ROWS - 1 and not piece.is_king:
            piece.make_king()
            self.black_kings += 1

    def remove_piece(self, pieces_to_remove: list[tuple[int, int]]) -> None:
        """Удаляет побитые шашку."""
        for row, col in pieces_to_remove:
            piece = self.grid[row][col]
            if piece:
                if piece.color == Color.WHITE:
                    self.white_left -= 1
                else:
                    self.black_left -= 1
            self.grid[row][col] = None

    def get_piece_position(self, piece: Piece) -> tuple[int, int]:
        """Вспомогательный метод: ищет координаты шашки на доске."""
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == piece:
                    return r, c
        return -1, -1

    def get_valid_moves(self, piece: Piece) -> dict:
        """Генерирует все возможные ходы: тихие шаги и прыжки (с учетом дамок)."""
        moves = {}
        row, col = self.get_piece_position(piece)
        if row == -1:
            return moves

        # 1. ОБЫЧНЫЕ ХОДЫ (без взятия)
        step_directions = []
        if piece.color == Color.WHITE or piece.is_king:
            step_directions.extend([(-1, -1), (-1, 1)])
        if piece.color == Color.BLACK or piece.is_king:
            step_directions.extend([(1, -1), (1, 1)])

        for dr, dc in step_directions:
            r, c = row + dr, col + dc

            while 0 <= r < ROWS and 0 <= c < COLS:
                if self.grid[r][c] is None:
                    moves[(r, c)] = []
                    if not piece.is_king:
                        break
                else:
                    break

                r += dr
                c += dc

        jump_moves = self._find_jumps(piece, row, col)
        moves.update(jump_moves)

        return moves

    def _find_jumps(self, piece: Piece, curr_row: int, curr_col: int, current_skipped: list = None,
                    moves: dict = None) -> dict:
        """Ищет прыжки. Для дамок просматривает весь луч."""
        if current_skipped is None:
            current_skipped = []
        if moves is None:
            moves = {}

        jump_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        start_row, start_col = self.get_piece_position(piece)

        for dr, dc in jump_directions:
            if piece.is_king:
                r, c = curr_row + dr, curr_col + dc
                enemy_found = False
                enemy_pos = None

                while 0 <= r < ROWS and 0 <= c < COLS:
                    target = self.grid[r][c]

                    if not enemy_found:
                        if target is not None:
                            if target.color == piece.color or (r, c) in current_skipped:
                                break
                            else:
                                enemy_found = True
                                enemy_pos = (r, c)
                    else:
                        if target is None or (r == start_row and c == start_col):
                            new_skipped = current_skipped + [enemy_pos]

                            if (r, c) not in moves or len(moves[(r, c)]) < len(new_skipped):
                                moves[(r, c)] = new_skipped

                            self._find_jumps(piece, r, c, new_skipped, moves)
                        else:
                            break

                    r += dr
                    c += dc

            else:
                enemy_r, enemy_c = curr_row + dr, curr_col + dc
                land_r, land_c = curr_row + dr * 2, curr_col + dc * 2

                if 0 <= land_r < ROWS and 0 <= land_c < COLS:
                    target = self.grid[enemy_r][enemy_c]

                    if target is not None and target.color != piece.color and (enemy_r, enemy_c) not in current_skipped:
                        if self.grid[land_r][land_c] is None or (land_r == start_row and land_c == start_col):
                            new_skipped = current_skipped + [(enemy_r, enemy_c)]

                            if (land_r, land_c) not in moves or len(moves[(land_r, land_c)]) < len(new_skipped):
                                moves[(land_r, land_c)] = new_skipped

                            self._find_jumps(piece, land_r, land_c, new_skipped, moves)
        return moves

    def winner(self) -> Optional[Color]:
        """Возвращает цвет победителя или None, если игра продолжается."""
        if self.white_left <= 0:
            return Color.BLACK
        elif self.black_left <= 0:
            return Color.WHITE
        return None