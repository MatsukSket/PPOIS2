from typing import Optional, List
from core.enums import Color
from core.piece import Piece
from app.consts import ROWS, COLS


class Board:
    """Представление логической матрицы доски и правил игры."""

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
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.grid[row][col]
        return None

    def get_piece_position(self, piece: Piece) -> tuple[int, int]:
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == piece:
                    return r, c
        return -1, -1

    def move_piece(self, piece: Piece, start_row: int, start_col: int, end_row: int, end_col: int) -> None:
        """Перемещает шашку в матрице и проверяет превращение в дамку."""
        self.grid[start_row][start_col], self.grid[end_row][end_col] = self.grid[end_row][end_col], \
        self.grid[start_row][start_col]

        if not piece.is_king:
            if (piece.color == Color.WHITE and end_row == 0) or \
                    (piece.color == Color.BLACK and end_row == ROWS - 1):
                piece.make_king()
                if piece.color == Color.WHITE:
                    self.white_kings += 1
                else:
                    self.black_kings += 1

    def remove_piece(self, pieces_to_remove: list[tuple[int, int]]) -> None:
        """Удаляет срубленные шашки с доски."""
        for row, col in pieces_to_remove:
            piece = self.grid[row][col]
            if piece:
                if piece.color == Color.WHITE:
                    self.white_left -= 1
                else:
                    self.black_left -= 1
            self.grid[row][col] = None

    def winner(self) -> Optional[Color]:
        if self.white_left <= 0: return Color.BLACK
        if self.black_left <= 0: return Color.WHITE
        return None


    def get_valid_moves(self, piece: Piece) -> dict:
        """Возвращает все разрешенные ходы для конкретной шашки."""
        row, col = self.get_piece_position(piece)
        if row == -1:
            return {}

        jump_moves = self._find_jumps(piece, row, col)

        if jump_moves:
            return jump_moves

        return self._get_step_moves(piece, row, col)

    def _get_step_moves(self, piece: Piece, row: int, col: int) -> dict:
        """Ищет тихие ходы (без взятия врага)."""
        moves = {}
        directions = []
        if piece.color == Color.WHITE or piece.is_king:
            directions.extend([(-1, -1), (-1, 1)])
        if piece.color == Color.BLACK or piece.is_king:
            directions.extend([(1, -1), (1, 1)])

        for dr, dc in directions:
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
        return moves

    def _find_jumps(self, piece: Piece, row: int, col: int, skipped: list = None, moves: dict = None) -> dict:
        """Диспетчер поиска прыжков. Разделяет логику для простых шашек и дамок."""
        skipped = skipped or []
        moves = moves or {}
        start_r, start_c = self.get_piece_position(piece)

        if piece.is_king:
            self._find_king_jumps(piece, row, col, start_r, start_c, skipped, moves)
        else:
            self._find_regular_jumps(piece, row, col, start_r, start_c, skipped, moves)

        return moves

    def _find_regular_jumps(self, piece: Piece, row: int, col: int, start_r: int, start_c: int, skipped: list,
                            moves: dict):
        """Рекурсивный поиск рубок для обычной шашки."""
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            enemy_r, enemy_c = row + dr, col + dc
            land_r, land_c = enemy_r + dr, enemy_c + dc

            if 0 <= land_r < ROWS and 0 <= land_c < COLS:
                target = self.grid[enemy_r][enemy_c]
                landing = self.grid[land_r][land_c]

                if target and target.color != piece.color and (enemy_r, enemy_c) not in skipped:
                    if landing is None or (land_r == start_r and land_c == start_c):
                        new_skipped = skipped + [(enemy_r, enemy_c)]

                        if (land_r, land_c) not in moves or len(moves[(land_r, land_c)]) < len(new_skipped):
                            moves[(land_r, land_c)] = new_skipped

                        self._find_regular_jumps(piece, land_r, land_c, start_r, start_c, new_skipped, moves)

    def _find_king_jumps(self, piece: Piece, row: int, col: int, start_r: int, start_c: int, skipped: list,
                         moves: dict):
        """Рекурсивный поиск рубок для 'летающей' дамки."""
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            enemy_pos = None

            while 0 <= r < ROWS and 0 <= c < COLS:
                target = self.grid[r][c]

                if not enemy_pos:
                    if target:
                        if target.color == piece.color or (r, c) in skipped:
                            break
                        enemy_pos = (r, c)

                else:
                    if target is None or (r == start_r and c == start_c):
                        new_skipped = skipped + [enemy_pos]

                        if (r, c) not in moves or len(moves[(r, c)]) < len(new_skipped):
                            moves[(r, c)] = new_skipped

                        self._find_king_jumps(piece, r, c, start_r, start_c, new_skipped, moves)
                    else:
                        break

                r += dr
                c += dc