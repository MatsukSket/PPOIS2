import pygame
from app.consts import *
from core.board import Board
from core.enums import Color


class Renderer:
    """Отвечает за визуализацию всех элементов игры с помощью модуля Pygame."""

    def __init__(self, screen):
        self.screen = screen

    def _get_visual_pos(self, row: int, col: int, flip_board: bool) -> tuple[int, int]:
        """Преобразует логические координаты матрицы в визуальные индексы."""
        if flip_board:
            return ROWS - 1 - row, COLS - 1 - col
        return row, col

    def draw_squares(self, flip_board: bool):
        """Отрисовывает шахматную сетку со сдвигом вниз и черной каймой."""
        pygame.draw.rect(self.screen, LIGHT_PLATE, (0, UI_HEIGHT, WINDOW_WIDTH, BOARD_SIZE))

        for row in range(ROWS):
            for col in range((row + 1) % 2, COLS, 2):
                v_row, v_col = self._get_visual_pos(row, col, flip_board)
                pygame.draw.rect(
                    self.screen, DARK_PLATE,
                    (v_col * TILE_SIZE, v_row * TILE_SIZE + UI_HEIGHT, TILE_SIZE, TILE_SIZE)
                )

        pygame.draw.rect(self.screen, (0, 0, 0), (0, UI_HEIGHT, WINDOW_WIDTH, BOARD_SIZE), 2)

    def draw_pieces(self, board: Board, flip_board: bool, ignore_pos: tuple = None):
        """Отрисовывает все шашки на доске (позволяет скрыть одну во время анимации)."""
        for row in range(ROWS):
            for col in range(COLS):
                if ignore_pos and (row, col) == ignore_pos:
                    continue

                piece = board.get_piece(row, col)
                if piece:
                    v_row, v_col = self._get_visual_pos(row, col, flip_board)
                    x = v_col * TILE_SIZE + TILE_SIZE // 2
                    y = v_row * TILE_SIZE + TILE_SIZE // 2 + UI_HEIGHT

                    color = WHITE_PIECE if piece.color == Color.WHITE else BLACK_PIECE
                    pygame.draw.circle(self.screen, color, (x, y), PIECE_RADIUS)
                    pygame.draw.circle(self.screen, PIECE_BORDER, (x, y), PIECE_RADIUS, PIECE_BORDER_WIDTH)

                    if piece.is_king:
                        pygame.draw.circle(self.screen, GOLD, (x, y), PIECE_RADIUS - 15)

    def draw_board(self, board: Board, controller=None, flip_board: bool = False):
        """Главный метод отрисовки игрового кадра (доска, шашки, интерфейс)."""
        self.draw_squares(flip_board)

        if controller and controller.selected:
            r, c = board.get_piece_position(controller.selected)
            if r != -1:
                v_row, v_col = self._get_visual_pos(r, c, flip_board)
                pygame.draw.rect(
                    self.screen, HIGHLIGHT_TILE,
                    (v_col * TILE_SIZE, v_row * TILE_SIZE + UI_HEIGHT, TILE_SIZE, TILE_SIZE)
                )

        self.draw_pieces(board, flip_board)
        self.draw_valid_moves(controller, flip_board)
        self.draw_game_ui()
        pygame.display.update()

    def draw_valid_moves(self, controller, flip_board: bool):
        """Отрисовывает маркеры-подсказки на клетках доступных ходов."""
        if controller and controller.valid_moves:
            for move in controller.valid_moves:
                row, col = move
                v_row, v_col = self._get_visual_pos(row, col, flip_board)
                x = v_col * TILE_SIZE + TILE_SIZE // 2
                y = v_row * TILE_SIZE + TILE_SIZE // 2 + UI_HEIGHT
                pygame.draw.circle(self.screen, POSSIBLE_MOVE, (x, y), POSSIBLE_MOVE_RADIUS)

    def draw_game_ui(self):
        """Отрисовывает верхнюю панель и элементы UI на ней."""
        pygame.draw.rect(self.screen, UI_BG_COLOR, (0, 0, WINDOW_WIDTH, UI_HEIGHT))

        pygame.draw.rect(self.screen, BUTTON_COLOR, PAUSE_BTN_RECT, border_radius=10)
        pygame.draw.rect(self.screen, TEXT_COLOR, PAUSE_BTN_RECT, width=2, border_radius=10)

        font = pygame.font.SysFont("comicsans", 30)
        text = font.render("Пауза", True, TEXT_COLOR)
        x = PAUSE_BTN_RECT.x + (PAUSE_BTN_RECT.width - text.get_width()) // 2
        y = PAUSE_BTN_RECT.y + (PAUSE_BTN_RECT.height - text.get_height()) // 2
        self.screen.blit(text, (x, y))

    def animate_move(self, piece, start_pos, end_pos, board, flip_board, clock):
        """Создает плавную анимацию перемещения шашки из start_pos в end_pos."""
        start_r, start_c = start_pos
        end_r, end_c = end_pos

        v_start_r, v_start_c = self._get_visual_pos(start_r, start_c, flip_board)
        v_end_r, v_end_c = self._get_visual_pos(end_r, end_c, flip_board)

        start_x = v_start_c * TILE_SIZE + TILE_SIZE // 2
        start_y = v_start_r * TILE_SIZE + TILE_SIZE // 2 + UI_HEIGHT
        end_x = v_end_c * TILE_SIZE + TILE_SIZE // 2
        end_y = v_end_r * TILE_SIZE + TILE_SIZE // 2 + UI_HEIGHT

        frames = 15
        dx = (end_x - start_x) / frames
        dy = (end_y - start_y) / frames

        for i in range(frames + 1):
            clock.tick(60)

            self.draw_squares(flip_board)
            self.draw_pieces(board, flip_board, ignore_pos=(start_r, start_c))
            self.draw_game_ui()

            curr_x = start_x + dx * i
            curr_y = start_y + dy * i

            color = WHITE_PIECE if piece.color == Color.WHITE else BLACK_PIECE
            pygame.draw.circle(self.screen, color, (int(curr_x), int(curr_y)), PIECE_RADIUS)
            pygame.draw.circle(self.screen, PIECE_BORDER, (int(curr_x), int(curr_y)), PIECE_RADIUS, PIECE_BORDER_WIDTH)
            if piece.is_king:
                pygame.draw.circle(self.screen, GOLD, (int(curr_x), int(curr_y)), PIECE_RADIUS - 15)

            pygame.display.update()