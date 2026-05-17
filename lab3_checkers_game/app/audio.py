import pygame
import os


class AudioManager:
    """Управляет загрузкой и воспроизведением звуков и музыки."""

    def __init__(self):
        pygame.mixer.init()
        self.move_sound = self._load_sound("move.wav")
        self.capture_sound = self._load_sound("capture.wav")
        self.king_sound = self._load_sound("king.wav")
        self.bg_music_path = os.path.join("assets", "background.mp3")

    def _load_sound(self, filename: str):
        path = os.path.join("assets", filename)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.5)
            return sound
        return None

    def play_bg_music(self):
        """Запускает фоновую музыку по кругу."""
        if os.path.exists(self.bg_music_path):
            pygame.mixer.music.load(self.bg_music_path)
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)
        else:
            print(f"Предупреждение: фоновая музыка {self.bg_music_path} не найдена.")

    def stop_bg_music(self):
        pygame.mixer.music.stop()

    def play_move(self):
        if self.move_sound: self.move_sound.play()

    def play_capture(self):
        if self.capture_sound: self.capture_sound.play()

    def play_king(self):
        if self.king_sound: self.king_sound.play()