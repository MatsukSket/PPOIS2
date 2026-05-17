import pygame
import os

class AudioManager:
    """Управляет загрузкой и воспроизведением звуковых эффектов."""

    def __init__(self):
        # Инициализируем аудио-модуль Pygame
        pygame.mixer.init()

        # Загружаем звуки (если файлов нет, программа не упадет, а просто оставит None)
        self.move_sound = self._load_sound("move.wav")
        self.capture_sound = self._load_sound("capture.wav")
        self.king_sound = self._load_sound("king.wav")

    def _load_sound(self, filename: str):
        path = os.path.join("assets", filename)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.5)  # Громкость 50%
            return sound
        print(f"Предупреждение: звук {path} не найден.")
        return None

    def play_move(self):
        if self.move_sound: self.move_sound.play()

    def play_capture(self):
        if self.capture_sound: self.capture_sound.play()

    def play_king(self):
        if self.king_sound: self.king_sound.play()