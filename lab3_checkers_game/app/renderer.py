import pygame
from app.consts import cfg, ROWS, COLS
from core.board import Board
from core.enums import Color


class Renderer:
    """Отвечает за визуализацию игры с поддержкой адаптивных размеров поля."""

    def __init__(self, screen):
        self.screen = screen

    def _get_visual_pos(self, row: int, col: int, flip_board: bool) -> tuple[int, int]:
        """Возвращает логические индексы клетки с учетом переворота доски."""
        if flip_board:
            return ROWS - 1 - row, COLS - 1 - col
        return row, col

    def _get_tile_rect(self, row: int, col: int, flip_board: bool) -> pygame.Rect:
        """Возвращает прямоугольник (Rect) для конкретной клетки."""
        v_row, v_col = self._get_visual_pos(row, col, flip_board)
        x = cfg.BOARD_OFFSET_X + v_col * cfg.TILE_SIZE
        y = cfg.BOARD_OFFSET_Y + v_row * cfg.TILE_SIZE
        return pygame.Rect(x, y, cfg.TILE_SIZE, cfg.TILE_SIZE)

    def _get_pixel_center(self, row: int, col: int, flip_board: bool) -> tuple[int, int]:
        """Возвращает координаты центра клетки в пикселях (x, y)."""
        rect = self._get_tile_rect(row, col, flip_board)
        return rect.centerx, rect.centery

    def _draw_single_piece(self, piece, x: int, y: int, radius: int = None):
        """Универсальный метод для отрисовки одной шашки (с короной и обводкой)."""
        if radius is None:
            radius = cfg.PIECE_RADIUS

        color = cfg.WHITE_PIECE if piece.color == Color.WHITE else cfg.BLACK_PIECE
        border_width = min(cfg.PIECE_BORDER_WIDTH, radius)  # Чтобы обводка не ломалась при сужении радиуса

        pygame.draw.circle(self.screen, color, (x, y), radius)
        if border_width > 0:
            pygame.draw.circle(self.screen, cfg.PIECE_BORDER, (x, y), radius, border_width)

        if piece.is_king and radius > 15:
            pygame.draw.circle(self.screen, cfg.GOLD, (x, y), max(2, radius - 15))


    def draw_squares(self, flip_board: bool):
        self.screen.fill(cfg.UI_BG_COLOR)

        pygame.draw.rect(self.screen, cfg.LIGHT_PLATE,
                         (cfg.BOARD_OFFSET_X, cfg.BOARD_OFFSET_Y, cfg.BOARD_SIZE, cfg.BOARD_SIZE))

        for row in range(ROWS):
            for col in range((row + 1) % 2, COLS, 2):
                rect = self._get_tile_rect(row, col, flip_board)
                pygame.draw.rect(self.screen, cfg.DARK_PLATE, rect)

        pygame.draw.rect(self.screen, (0, 0, 0),
                         (cfg.BOARD_OFFSET_X, cfg.BOARD_OFFSET_Y, cfg.BOARD_SIZE, cfg.BOARD_SIZE), 2)

    def draw_pieces(self, board: Board, flip_board: bool, ignore_pos=None):
        ignore_list = [ignore_pos] if isinstance(ignore_pos, tuple) else (ignore_pos or [])

        for row in range(ROWS):
            for col in range(COLS):
                if (row, col) in ignore_list:
                    continue
                piece = board.get_piece(row, col)
                if piece:
                    x, y = self._get_pixel_center(row, col, flip_board)
                    self._draw_single_piece(piece, x, y)

    def draw_board(self, board: Board, controller=None, flip_board: bool = False):
        self.draw_squares(flip_board)

        if controller and controller.selected:
            r, c = board.get_piece_position(controller.selected)
            if r != -1:
                rect = self._get_tile_rect(r, c, flip_board)
                pygame.draw.rect(self.screen, cfg.HIGHLIGHT_TILE, rect)

        self.draw_pieces(board, flip_board)
        self.draw_valid_moves(controller, flip_board)
        self.draw_game_ui()
        pygame.display.update()

    def draw_valid_moves(self, controller, flip_board: bool):
        if controller and controller.valid_moves:
            for move in controller.valid_moves:
                row, col = move
                x, y = self._get_pixel_center(row, col, flip_board)
                pygame.draw.circle(self.screen, cfg.POSSIBLE_MOVE, (x, y), cfg.POSSIBLE_MOVE_RADIUS)

    def draw_game_ui(self):
        pygame.draw.rect(self.screen, cfg.UI_BG_COLOR, (0, 0, cfg.ACTUAL_WIDTH, cfg.UI_HEIGHT))
        pygame.draw.rect(self.screen, cfg.BUTTON_COLOR, cfg.PAUSE_BTN_RECT, border_radius=10)
        pygame.draw.rect(self.screen, cfg.TEXT_COLOR, cfg.PAUSE_BTN_RECT, width=2, border_radius=10)

        font = pygame.font.SysFont("comicsans", 30)
        text = font.render("Пауза", True, cfg.TEXT_COLOR)
        x = cfg.PAUSE_BTN_RECT.x + (cfg.PAUSE_BTN_RECT.width - text.get_width()) // 2
        y = cfg.PAUSE_BTN_RECT.y + (cfg.PAUSE_BTN_RECT.height - text.get_height()) // 2
        self.screen.blit(text, (x, y))


    def animate_move(self, piece, start_pos, end_pos, board, flip_board, clock):
        start_x, start_y = self._get_pixel_center(*start_pos, flip_board)
        end_x, end_y = self._get_pixel_center(*end_pos, flip_board)

        frames = 15
        dx = (end_x - start_x) / frames
        dy = (end_y - start_y) / frames

        for i in range(frames + 1):
            clock.tick(cfg.FPS)
            self.draw_squares(flip_board)
            self.draw_pieces(board, flip_board, ignore_pos=start_pos)
            self.draw_game_ui()

            curr_x = int(start_x + dx * i)
            curr_y = int(start_y + dy * i)

            self._draw_single_piece(piece, curr_x, curr_y)
            pygame.display.update()

    def animate_capture(self, skipped: list, board: Board, flip_board: bool, clock):
        frames = 15
        for i in range(frames + 1):
            clock.tick(cfg.FPS)
            self.draw_squares(flip_board)
            self.draw_pieces(board, flip_board, ignore_pos=skipped)
            self.draw_game_ui()

            radius = max(0, int(cfg.PIECE_RADIUS * (1 - i / frames)))

            for row, col in skipped:
                piece = board.get_piece(row, col)
                if piece and radius > 0:
                    x, y = self._get_pixel_center(row, col, flip_board)
                    self._draw_single_piece(piece, x, y, radius)

            pygame.display.update()