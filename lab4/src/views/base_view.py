from abc import ABC, abstractmethod
from typing import Callable, List, Tuple
from src.models import Shop, Product, Customer


class BaseView(ABC):
    """Абстрактный класс для всех графических и консольных представлений."""

    @abstractmethod
    def start(self) -> None:
        """Запуск цикла интерфейса."""
        pass

    @abstractmethod
    def show_message(self, message: str) -> None:
        """Отображение успешного действия или информации."""
        pass

    @abstractmethod
    def show_error(self, error: str) -> None:
        """Отображение ошибки."""
        pass

    @abstractmethod
    def update_customer_info(self, customer: Customer) -> None:
        """Обновление данных покупателя на экране (баланс, статус акций)."""
        pass

    @abstractmethod
    def show_search_results(self, results: List[Tuple[Shop, Product]]) -> None:
        """Отображение результатов поиска."""
        pass

    @abstractmethod
    def show_purchased_items(self, items: List[Product]) -> None:
        """Отображение списка купленных товаров."""
        pass


    @abstractmethod
    def bind_search(self, callback: Callable[[str], None]) -> None:
        pass

    @abstractmethod
    def bind_purchase(self, callback: Callable[[str, int], None]) -> None:
        pass

    @abstractmethod
    def bind_toggle_promotion(self, callback: Callable[[], None]) -> None:
        pass

    @abstractmethod
    def bind_rate_service(self, callback: Callable[[str, float], None]) -> None:
        pass

    @abstractmethod
    def bind_view_purchases(self, callback: Callable[[], None]) -> None:
        pass