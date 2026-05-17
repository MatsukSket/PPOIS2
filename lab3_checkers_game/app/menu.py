import pygame
from app.consts import *
from core.enums import PlayerMode, Color


class Menu:
    """Базовый класс для всех экранов меню в игре."""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("comicsans", 40)
        self.title_font = pygame.font.SysFont("comicsans", 70)

        btn_width, btn_height = 400, 80
        center_x = BOARD_SIZE // 2 - btn_width // 2
        self.btn_single = pygame.Rect(center_x, 300, btn_width, btn_height)
        self.btn_two_players = pygame.Rect(center_x, 420, btn_width, btn_height)

    def _draw_overlay(self, alpha: int = 150):
        """Рисует полупрозрачный слой поверх текущего экрана для акцентирования внимания на меню."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def _draw_button(self, rect: pygame.Rect, text: str, mouse_pos: tuple):
        """Отрисовывает интерактивную кнопку с учетом наведения мыши (hover-эффект)."""
        color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=15)
        pygame.draw.rect(self.screen, TEXT_COLOR, rect, width=3, border_radius=15)

        text_surf = self.font.render(text, True, TEXT_COLOR)
        text_x = rect.x + (rect.width - text_surf.get_width()) // 2
        text_y = rect.y + (rect.height - text_surf.get_height()) // 2
        self.screen.blit(text_surf, (text_x, text_y))

    def draw(self):
        """Отрисовывает главное (стартовое) меню игры."""
        self.screen.fill(LIGHT_PLATE)
        title_text = self.title_font.render("ШАШКИ", True, TEXT_COLOR)
        self.screen.blit(title_text, (BOARD_SIZE // 2 - title_text.get_width() // 2, 100))

        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(self.btn_single, "Игра с собой", mouse_pos)
        self._draw_button(self.btn_two_players, "Игра на двоих", mouse_pos)
        pygame.display.update()

    def handle_click(self, pos: tuple) -> PlayerMode | None:
        """Возвращает выбранный режим игры при клике по соответствующей кнопке."""
        if self.btn_single.collidepoint(pos): return PlayerMode.SINGLE
        if self.btn_two_players.collidepoint(pos): return PlayerMode.VERSUS
        return None


class PauseMenu(Menu):
    """Экран паузы, отображаемый поверх игрового процесса."""

    def __init__(self, screen):
        super().__init__(screen)
        btn_w, btn_h = 300, 70
        cx = BOARD_SIZE // 2 - btn_w // 2
        self.btn_resume = pygame.Rect(cx, 250, btn_w, btn_h)
        self.btn_restart = pygame.Rect(cx, 350, btn_w, btn_h)
        self.btn_menu = pygame.Rect(cx, 450, btn_w, btn_h)

    def draw(self):
        """Отрисовывает меню паузы с затемнением фона."""
        self._draw_overlay()
        title = self.title_font.render("ПАУЗА", True, WHITE_PIECE)
        self.screen.blit(title, (BOARD_SIZE // 2 - title.get_width() // 2, 100))

        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(self.btn_resume, "Продолжить", mouse_pos)
        self._draw_button(self.btn_restart, "Рестарт", mouse_pos)
        self._draw_button(self.btn_menu, "В меню", mouse_pos)
        pygame.display.update()

    def handle_click(self, pos: tuple) -> str | None:
        """Возвращает строковой идентификатор выбранного действия в меню паузы."""
        if self.btn_resume.collidepoint(pos): return "RESUME"
        if self.btn_restart.collidepoint(pos): return "RESTART"
        if self.btn_menu.collidepoint(pos): return "MENU"
        return None


class GameOverMenu(Menu):
    """Экран завершения партии, объявляющий победителя."""

    def __init__(self, screen):
        super().__init__(screen)
        btn_w, btn_h = 300, 70
        cx = BOARD_SIZE // 2 - btn_w // 2
        self.btn_restart = pygame.Rect(cx, 350, btn_w, btn_h)
        self.btn_menu = pygame.Rect(cx, 450, btn_w, btn_h)

    def draw(self, winner: Color):
        """Отрисовывает экран победителя поверх последнего состояния доски."""
        self._draw_overlay(alpha=180)
        text = "БЕЛЫЕ ПОБЕДИЛИ!" if winner == Color.WHITE else "ЧЕРНЫЕ ПОБЕДИЛИ!"
        title = self.title_font.render(text, True, WHITE_PIECE)
        self.screen.blit(title, (BOARD_SIZE // 2 - title.get_width() // 2, 150))

        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(self.btn_restart, "Играть еще", mouse_pos)
        self._draw_button(self.btn_menu, "В меню", mouse_pos)
        pygame.display.update()

    def handle_click(self, pos: tuple) -> str | None:
        """Возвращает строковой идентификатор действия после окончания игры."""
        if self.btn_restart.collidepoint(pos): return "RESTART"
        if self.btn_menu.collidepoint(pos): return "MENU"
        return None