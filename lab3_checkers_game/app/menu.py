import pygame
from app.consts import cfg
from core.enums import PlayerMode, Color


class BaseMenu:
    """Чистый базовый класс для всех экранов меню."""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("comicsans", 40)
        self.title_font = pygame.font.SysFont("comicsans", 70)
        self.buttons = {}  # Словарь для автоматической обработки кликов {action: rect}
        self.update_buttons()

    def update_buttons(self):
        """Переопределяется в наследниках для создания кнопок."""
        pass

    def _create_vertical_layout(self, actions: list[str], start_y: int, spacing: int = 75, btn_w: int = 400,
                                btn_h: int = 60):
        """Автоматически выстраивает кнопки в колонку по центру."""
        self.buttons.clear()
        cx = cfg.ACTUAL_WIDTH // 2 - btn_w // 2

        for i, action in enumerate(actions):
            self.buttons[action] = pygame.Rect(cx, start_y + i * spacing, btn_w, btn_h)

    def _draw_overlay(self, alpha: int = 150):
        overlay = pygame.Surface((cfg.ACTUAL_WIDTH, cfg.ACTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def _draw_title(self, text: str, color=None, y_offset: int = 60):
        """Универсальная отрисовка заголовка по центру."""
        color = color or cfg.TEXT_COLOR
        title = self.title_font.render(text, True, color)
        self.screen.blit(title, (cfg.ACTUAL_WIDTH // 2 - title.get_width() // 2, y_offset))

    def _draw_button(self, rect: pygame.Rect, text: str, mouse_pos: tuple):
        color = cfg.BUTTON_HOVER if rect.collidepoint(mouse_pos) else cfg.BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=15)
        pygame.draw.rect(self.screen, cfg.TEXT_COLOR, rect, width=3, border_radius=15)

        text_surf = self.font.render(text, True, cfg.TEXT_COLOR)
        text_x = rect.x + (rect.width - text_surf.get_width()) // 2
        text_y = rect.y + (rect.height - text_surf.get_height()) // 2
        self.screen.blit(text_surf, (text_x, text_y))

    def draw(self):
        """Переопределяется в наследниках для отрисовки."""
        pass

    def handle_click(self, pos: tuple):
        """Автоматическая обработка кликов по словарю кнопок."""
        for action, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return action
        return None


class MainMenu(BaseMenu):
    def update_buttons(self):
        # Используем авто-верстку! Больше никакой ручной математики.
        actions = [PlayerMode.SINGLE, PlayerMode.VERSUS, "LEADERBOARD", "SETTINGS", "HELP", "QUIT"]
        self._create_vertical_layout(actions, start_y=180)

    def draw(self):
        self.screen.fill(cfg.LIGHT_PLATE)
        self._draw_title("ШАШКИ")

        mouse_pos = pygame.mouse.get_pos()
        labels = ["Игра с собой", "Игра на двоих", "Таблица рекордов", "Настройки", "Справка", "Выход"]

        for action, label in zip(self.buttons.keys(), labels):
            self._draw_button(self.buttons[action], label, mouse_pos)
        pygame.display.update()


class PauseMenu(BaseMenu):
    def update_buttons(self):
        self._create_vertical_layout(["RESUME", "RESTART", "MENU"], start_y=250, spacing=80, btn_w=300)

    def draw(self):
        self._draw_overlay()
        self._draw_title("ПАУЗА", color=cfg.WHITE_PIECE, y_offset=100)

        mouse_pos = pygame.mouse.get_pos()
        labels = {"RESUME": "Продолжить", "RESTART": "Рестарт", "MENU": "В меню"}

        for action, rect in self.buttons.items():
            self._draw_button(rect, labels[action], mouse_pos)
        pygame.display.update()


class GameOverMenu(BaseMenu):
    def update_buttons(self):
        self._create_vertical_layout(["RESTART", "MENU"], start_y=330, spacing=80, btn_w=300)

    def draw(self, winner: Color):
        self._draw_overlay(alpha=180)
        text = "БЕЛЫЕ ПОБЕДИЛИ!" if winner == Color.WHITE else "ЧЕРНЫЕ ПОБЕДИЛИ!"
        self._draw_title(text, color=cfg.WHITE_PIECE, y_offset=150)

        mouse_pos = pygame.mouse.get_pos()
        labels = {"RESTART": "Играть еще", "MENU": "В меню"}
        for action, rect in self.buttons.items():
            self._draw_button(rect, labels[action], mouse_pos)
        pygame.display.update()


class SettingsMenu(BaseMenu):
    def update_buttons(self):
        self._create_vertical_layout(["RES_1", "RES_2", "TOGGLE_FS", "BACK"], start_y=220, spacing=80)

    def draw(self):
        self.screen.fill(cfg.LIGHT_PLATE)
        self._draw_title("НАСТРОЙКИ", y_offset=100)

        mouse_pos = pygame.mouse.get_pos()
        fs_text = "Экран: Полный (Вкл)" if cfg.FULLSCREEN else "Экран: Оконный (Выкл)"
        labels = {"RES_1": "Размер: 800x880", "RES_2": "Размер: 1000x1080", "TOGGLE_FS": fs_text,
                  "BACK": "Назад в меню"}

        for action, rect in self.buttons.items():
            self._draw_button(rect, labels[action], mouse_pos)
        pygame.display.update()


class HelpMenu(BaseMenu):
    def update_buttons(self):
        self._create_vertical_layout(["BACK"], start_y=cfg.ACTUAL_HEIGHT - 100, btn_w=300)

    def draw(self):
        self.screen.fill(cfg.LIGHT_PLATE)
        self._draw_title("ПРАВИЛА ИГРЫ", y_offset=50)

        rules = [
            "1. Шашки ходят по диагонали на 1 клетку вперед.",
            "2. Бить назад РАЗРЕШАЕТСЯ.",
            "3. Дамка (достигшая края доски) ходит на любое",
            "   расстояние по свободной диагонали.",
            "4. Можно срубить несколько шашек за ход.",
            "5. Цель игры: срубить или запереть все шашки",
            "   противника."
        ]

        font = pygame.font.SysFont("comicsans", 30)
        y = 150
        for line in rules:
            text = font.render(line, True, cfg.TEXT_COLOR)
            self.screen.blit(text, (cfg.ACTUAL_WIDTH // 2 - text.get_width() // 2, y))
            y += 50

        self._draw_button(self.buttons["BACK"], "Понятно", pygame.mouse.get_pos())
        pygame.display.update()


class NameInputMenu(BaseMenu):
    def __init__(self, screen):
        super().__init__(screen)
        self.white_name = ""
        self.black_name = ""
        self.active_field = 0

    def update_buttons(self):
        # Здесь ручная верстка нужна, так как элементы нестандартные
        btn_w, btn_h = 400, 60
        cx = cfg.ACTUAL_WIDTH // 2 - btn_w // 2
        self.rect_white = pygame.Rect(cx, 250, btn_w, btn_h)
        self.rect_black = pygame.Rect(cx, 380, btn_w, btn_h)
        self.buttons["START"] = pygame.Rect(cx, 520, btn_w, btn_h)
        self.buttons["BACK"] = pygame.Rect(cx, 600, btn_w, btn_h)

    def draw(self):
        self.screen.fill(cfg.LIGHT_PLATE)
        self._draw_title("ВВОД ИМЕН", y_offset=80)

        mouse_pos = pygame.mouse.get_pos()

        # Мигающий курсор (мигает каждые 500 мс)
        cursor = "|" if pygame.time.get_ticks() % 1000 < 500 else ""

        # --- Поле белых ---
        label_w = self.font.render("Имя за Белых:", True, cfg.TEXT_COLOR)
        self.screen.blit(label_w, (self.rect_white.x, self.rect_white.y - label_w.get_height() - 5))
        color_w = cfg.HIGHLIGHT_TILE if self.active_field == 0 else cfg.BUTTON_COLOR
        pygame.draw.rect(self.screen, color_w, self.rect_white, border_radius=10)
        pygame.draw.rect(self.screen, cfg.TEXT_COLOR, self.rect_white, width=2, border_radius=10)
        text_w = self.font.render(self.white_name + (cursor if self.active_field == 0 else ""), True, cfg.TEXT_COLOR)
        self.screen.blit(text_w, (self.rect_white.x + 10, self.rect_white.y + 15))

        # --- Поле черных ---
        label_b = self.font.render("Имя за Черных:", True, cfg.TEXT_COLOR)
        self.screen.blit(label_b, (self.rect_black.x, self.rect_black.y - label_b.get_height() - 5))
        color_b = cfg.HIGHLIGHT_TILE if self.active_field == 1 else cfg.BUTTON_COLOR
        pygame.draw.rect(self.screen, color_b, self.rect_black, border_radius=10)
        pygame.draw.rect(self.screen, cfg.TEXT_COLOR, self.rect_black, width=2, border_radius=10)
        text_b = self.font.render(self.black_name + (cursor if self.active_field == 1 else ""), True, cfg.TEXT_COLOR)
        self.screen.blit(text_b, (self.rect_black.x + 10, self.rect_black.y + 15))

        self._draw_button(self.buttons["START"], "Начать битву", mouse_pos)
        self._draw_button(self.buttons["BACK"], "Назад", mouse_pos)
        pygame.display.update()

    def handle_click(self, pos: tuple):
        if self.rect_white.collidepoint(pos):
            self.active_field = 0
        elif self.rect_black.collidepoint(pos):
            self.active_field = 1
        return super().handle_click(pos)

    def handle_keydown(self, event):
        if event.key == pygame.K_BACKSPACE:
            if self.active_field == 0:
                self.white_name = self.white_name[:-1]
            else:
                self.black_name = self.black_name[:-1]
        elif event.key == pygame.K_TAB or event.key == pygame.K_RETURN:
            self.active_field = 1 if self.active_field == 0 else 0
        else:
            if len(event.unicode) > 0 and event.unicode.isprintable():
                if self.active_field == 0 and len(self.white_name) < 15:
                    self.white_name += event.unicode
                elif self.active_field == 1 and len(self.black_name) < 15:
                    self.black_name += event.unicode


class LeaderboardMenu(BaseMenu):
    def __init__(self, screen, record_manager):
        self.records = record_manager
        super().__init__(screen)  # Вызываем super после создания специфичных полей!

    def update_buttons(self):
        self._create_vertical_layout(["BACK"], start_y=cfg.ACTUAL_HEIGHT - 100, btn_w=300)

    def draw(self):
        self.screen.fill(cfg.LIGHT_PLATE)
        self._draw_title("ЗАЛ СЛАВЫ", y_offset=50)

        top_players = self.records.get_top(7)
        font = pygame.font.SysFont("comicsans", 35)

        y = 150
        if not top_players:
            text = font.render("Пока пусто. Станьте первым!", True, cfg.TEXT_COLOR)
            self.screen.blit(text, (cfg.ACTUAL_WIDTH // 2 - text.get_width() // 2, y))
        else:
            for i, (name, score) in enumerate(top_players):
                text = font.render(f"{i + 1}. {name}  ........  {score} очков", True, cfg.TEXT_COLOR)
                self.screen.blit(text, (cfg.ACTUAL_WIDTH // 2 - text.get_width() // 2, y))
                y += 50

        self._draw_button(self.buttons["BACK"], "Назад", pygame.mouse.get_pos())
        pygame.display.update()