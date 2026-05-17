import os
from src.services import MallServices
from src.models import Customer, ShoppingMall, ShoppingGallery, Shop, Seller, Product
from src.exceptions import ShoppingMallException


class MainPresenter:
    AUTO_SAVE_FILE = "mall_data.json"

    def __init__(self, services: MallServices, customer: Customer, view) -> None:
        self.services = services
        self.customer = customer
        self.view = view

        # Привязка базовых методов
        self.view.bind_search(self.handle_search)
        self.view.bind_purchase(self.handle_purchase)
        self.view.bind_toggle_promotion(self.handle_toggle_promotion)
        self.view.bind_rate_service(self.handle_rate_service)
        self.view.bind_view_purchases(self.handle_view_purchases)

        # Привязка CRUD методов
        self.view.bind_add_mall(self.handle_add_mall)
        self.view.bind_delete_mall(self.handle_delete_mall)
        self.view.bind_add_shop(self.handle_add_shop)
        self.view.bind_delete_shop(self.handle_delete_shop)
        self.view.bind_add_product(self.handle_add_product)
        self.view.bind_delete_product(self.handle_delete_product)

        # Привязка переключения и баланса
        self.view.bind_change_balance(self.handle_change_balance)
        self.view.bind_select_mall(self.handle_select_mall)  # НОВОЕ: Отслеживание выбора ТЦ в дереве

        self._initialize_data()

    def _initialize_data(self):
        if os.path.exists(self.AUTO_SAVE_FILE):
            try:
                self.customer = self.services.load_from_json(self.AUTO_SAVE_FILE)
            except Exception as e:
                self.view.show_error(f"Ошибка автозагрузки: {e}")
        else:
            self._auto_save()

        self.view.update_customer_info(self.customer)
        self.view.refresh_all_data(self.services.malls, self.services.active_mall)

    def _auto_save(self):
        try:
            self.services.save_to_json(self.AUTO_SAVE_FILE, self.customer)
        except Exception as e:
            self.view.show_error(f"Ошибка автосохранения: {e}")

    def run(self) -> None:
        self.view.start()
        self._auto_save()

    def handle_select_mall(self, name: str):
        """Переключает активный ТЦ при выборе его элементов в GUI."""
        if name in self.services.malls and self.services.active_mall != self.services.malls[name]:
            self.services.active_mall = self.services.malls[name]
            # Обновляем только список магазинов для постраничного вида
            self.view.update_paged_view_shops(self.services.active_mall)

    def handle_search(self, query: str) -> None:
        self.view.show_search_results(self.services.search_product(query))

    def handle_purchase(self, shop_name: str, product_id: int) -> None:
        try:
            self.services.purchase_item(self.customer, shop_name, product_id)
            self.view.show_message("Покупка успешна!")
            self.view.update_customer_info(self.customer)
            self.view.refresh_all_data(self.services.malls, self.services.active_mall)
            self._auto_save()
        except Exception as e:
            self.view.show_error(str(e))

    def handle_change_balance(self, amount: float) -> None:
        try:
            self.customer.balance = amount
            self.view.update_customer_info(self.customer)
            self._auto_save()
            self.view.show_message(f"Баланс успешно изменен на ${amount:.2f}")
        except Exception as e:
            self.view.show_error(str(e))

    def handle_toggle_promotion(self) -> None:
        self.services.toggle_promotion_participation(self.customer)
        self.view.update_customer_info(self.customer)
        self._auto_save()

    def handle_rate_service(self, shop_name: str, rating: float) -> None:
        try:
            self.services.rate_service(shop_name, rating)
            self.view.show_message(f"Оценка {rating} добавлена.")
            self.view.refresh_all_data(self.services.malls, self.services.active_mall)
            self._auto_save()
        except Exception as e:
            self.view.show_error(str(e))

    def handle_view_purchases(self) -> None:
        self.view.show_purchased_items(self.customer.purchased_items)

    # --- CRUD Обработчики ---
    def handle_add_mall(self, name: str, capacity: int):
        new_mall = ShoppingMall(name, ShoppingGallery(capacity))
        self.services.add_mall(new_mall)
        self.services.active_mall = new_mall  # Автоматически делаем новый ТЦ активным при создании
        self.view.refresh_all_data(self.services.malls, self.services.active_mall)
        self._auto_save()

    def handle_delete_mall(self, name: str):
        try:
            self.services.remove_mall(name)
            self.view.refresh_all_data(self.services.malls, self.services.active_mall)
            self._auto_save()
        except Exception as e:
            self.view.show_error(str(e))

    def handle_add_shop(self, shop_name: str, seller_name: str):
        try:
            self.services.add_shop_to_active_gallery(Shop(shop_name, Seller(seller_name)))
            self.view.refresh_all_data(self.services.malls, self.services.active_mall)
            self._auto_save()
        except Exception as e:
            self.view.show_error(str(e))

    def handle_delete_shop(self, shop_name: str):
        try:
            self.services.remove_shop_from_active_gallery(shop_name)
            self.view.refresh_all_data(self.services.malls, self.services.active_mall)
            self._auto_save()
        except Exception as e:
            self.view.show_error(str(e))

    def handle_add_product(self, shop_name: str, p_id: int, p_name: str, price: float, stock: int):
        try:
            self.services.add_product_to_shop(shop_name, Product(p_id, p_name, price, stock))
            self.view.refresh_all_data(self.services.malls, self.services.active_mall)
            self._auto_save()
        except Exception as e:
            self.view.show_error(str(e))

    def handle_delete_product(self, shop_name: str, p_id: int):
        try:
            self.services.remove_product_from_shop(shop_name, p_id)
            self.view.refresh_all_data(self.services.malls, self.services.active_mall)
            self._auto_save()
        except Exception as e:
            self.view.show_error(str(e))