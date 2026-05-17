import json
import os
import pygame

CONFIG_PATH = "config.json"

ROWS = 8
COLS = 8


class GameConfig:
    def __init__(self):
        self.default_settings = {
            "WINDOW_WIDTH": 800,
            "WINDOW_HEIGHT": 880,
            "UI_HEIGHT": 80,
            "FULLSCREEN": False,
            "FPS": 60,
            "WHITE_PIECE": [249, 249, 249],
            "BLACK_PIECE": [92, 89, 87],
            "PIECE_BORDER": [37, 35, 33],
            "GOLD": [255, 215, 0],
            "DARK_PLATE": [115, 149, 82],
            "LIGHT_PLATE": [235, 236, 208],
            "HIGHLIGHT_TILE": [185, 202, 66],
            "POSSIBLE_MOVE": [99, 128, 70],
            "UI_BG_COLOR": [210, 210, 210],
            "BUTTON_COLOR": [200, 200, 200],
            "BUTTON_HOVER": [170, 170, 170],
            "TEXT_COLOR": [0, 0, 0]
        }
        self.data = {}
        self.ACTUAL_WIDTH = 800
        self.ACTUAL_HEIGHT = 880
        self.load()

    def load(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    self.data = {**self.default_settings, **json.load(f)}
            except Exception:
                self.data = self.default_settings.copy()
        else:
            self.data = self.default_settings.copy()
            self.save()
        self.update_sizes()

    def save(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.data, f, indent=4)

    def update_sizes(self, actual_w=None, actual_h=None):
        """Пересчитывает размеры. Если переданы реальные размеры окна (например, от Fullscreen), использует их."""
        self.ACTUAL_WIDTH = actual_w if actual_w else self.data["WINDOW_WIDTH"]
        self.ACTUAL_HEIGHT = actual_h if actual_h else self.data["WINDOW_HEIGHT"]

        available_w = self.ACTUAL_WIDTH
        available_h = self.ACTUAL_HEIGHT - self.data["UI_HEIGHT"]

        self.BOARD_SIZE = min(available_w, available_h)
        self.TILE_SIZE = self.BOARD_SIZE // COLS

        # Центрирование по ДВУМ ОСЯМ!
        self.BOARD_OFFSET_X = (self.ACTUAL_WIDTH - self.BOARD_SIZE) // 2
        self.BOARD_OFFSET_Y = self.data["UI_HEIGHT"] + (available_h - self.BOARD_SIZE) // 2

        self.PIECE_RADIUS = self.TILE_SIZE // 2 - 8
        self.PIECE_BORDER_WIDTH = 3
        self.POSSIBLE_MOVE_RADIUS = self.TILE_SIZE // 5

        # Кнопка паузы теперь привязана к правому краю РЕАЛЬНОГО экрана
        self.PAUSE_BTN_RECT = pygame.Rect(self.ACTUAL_WIDTH - 140, (self.data["UI_HEIGHT"] - 40) // 2, 120, 40)

    # Проброс свойств данных
    @property
    def WINDOW_WIDTH(self):
        return self.data["WINDOW_WIDTH"]

    @property
    def WINDOW_HEIGHT(self):
        return self.data["WINDOW_HEIGHT"]

    @property
    def UI_HEIGHT(self):
        return self.data["UI_HEIGHT"]

    @property
    def FULLSCREEN(self):
        return self.data["FULLSCREEN"]

    @property
    def FPS(self):
        return self.data["FPS"]

    @property
    def WHITE_PIECE(self):
        return self.data["WHITE_PIECE"]

    @property
    def BLACK_PIECE(self):
        return self.data["BLACK_PIECE"]

    @property
    def PIECE_BORDER(self):
        return self.data["PIECE_BORDER"]

    @property
    def GOLD(self):
        return self.data["GOLD"]

    @property
    def DARK_PLATE(self):
        return self.data["DARK_PLATE"]

    @property
    def LIGHT_PLATE(self):
        return self.data["LIGHT_PLATE"]

    @property
    def HIGHLIGHT_TILE(self):
        return self.data["HIGHLIGHT_TILE"]

    @property
    def POSSIBLE_MOVE(self):
        return self.data["POSSIBLE_MOVE"]

    @property
    def UI_BG_COLOR(self):
        return self.data["UI_BG_COLOR"]

    @property
    def BUTTON_COLOR(self):
        return self.data["BUTTON_COLOR"]

    @property
    def BUTTON_HOVER(self):
        return self.data["BUTTON_HOVER"]

    @property
    def TEXT_COLOR(self):
        return self.data["TEXT_COLOR"]


cfg = GameConfig()