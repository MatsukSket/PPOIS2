from core.enums import Color


class Piece:
    """Модель шашки."""

    def __init__(self, color: Color):
        self.color = color
        self.is_king = False

    def make_king(self) -> None:
        """Превращает шашку в дамку."""
        self.is_king = True

    def __repr__(self) -> str:
        """Для удобной отладки в консоли."""
        role = "K" if self.is_king else "P"
        color_char = "W" if self.color == Color.WHITE else "B"
        return f"{role}{color_char}"