import sys
from src.models import Customer, ShoppingMall


class CLIView:
    def __init__(self):
        self._customer_cache: Customer = None
        self._malls_cache: dict = {}
        self._active_mall: ShoppingMall = None
        self._active_shop_name: str = None

        self._state = 0

        self._on_search = self._on_purchase = self._on_change_balance = self._on_select_mall = None
        self._on_toggle_promo = self._on_rate = self._on_view_purchases = None
        self._on_add_mall = self._on_delete_mall = self._on_add_shop = None
        self._on_delete_shop = self._on_add_product = self._on_delete_product = None

    def start(self) -> None:
        while True:
            if self._state == 0:
                self._render_malls()
            elif self._state == 1:
                self._render_shops()
            elif self._state == 2:
                self._render_products()



    def _render_malls(self):
        print("\n" + "=" * 50)
        if self._customer_cache:
            promo = "Вкл" if self._customer_cache.participates_in_promotions else "Выкл"
            print(
                f"Пользователь: {self._customer_cache.name} | Баланс: ${self._customer_cache.balance:.2f} | Акции: {promo}")
        print("--- СПИСОК ТОРГОВЫХ ЦЕНТРОВ ---")

        malls_list = list(self._malls_cache.values())
        if not malls_list:
            print("ТЦ отсутствуют. Добавьте первый Торговый Центр.")
        else:
            for idx, mall in enumerate(malls_list, 1):
                print(f"[{idx}] {mall.name} (Вместимость галереи: {mall.gallery.capacity})")

        print("-" * 50)
        print("[q] Добавить ТЦ      [w] Удалить ТЦ")
        print("[e] Изменить баланс  [r] Мои покупки")
        print("[t] Поиск товара     [y] Вкл/Выкл акции")
        print("[0] Выход из программы")

        choice = input("Выберите ТЦ (цифра) или действие (буква): ").strip().upper()

        if choice == '0':
            sys.exit(0)
        elif choice == 'Q' and self._on_add_mall:
            name = input("Название ТЦ: ").strip()
            cap = input("Вместимость галереи: ").strip()
            if cap.isdigit() and name: self._on_add_mall(name, int(cap))
        elif choice == 'W' and self._on_delete_mall:
            name = input("Название ТЦ для удаления: ").strip()
            self._on_delete_mall(name)
        elif choice == 'E' and self._on_change_balance:
            try:
                amt = float(input("Введите новый баланс: "))
                self._on_change_balance(amt)
            except ValueError:
                self.show_error("Баланс должен быть числом.")
        elif choice == 'R' and self._on_view_purchases:
            self._on_view_purchases()
        elif choice == 'T' and self._on_search:
            query = input("Введите название товара для поиска: ").strip()
            self._on_search(query)
        elif choice == 'Y' and self._on_toggle_promo:
            self._on_toggle_promo()
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(malls_list):
                mall_name = malls_list[idx].name
                if self._on_select_mall:
                    self._on_select_mall(mall_name)
                self._state = 1
            else:
                self.show_error("Неверный номер ТЦ.")

    def _render_shops(self):
        print("\n" + "=" * 50)
        if not self._active_mall:
            self._state = 0
            return

        print(f"ТЦ: {self._active_mall.name}")
        print("--- СПИСОК МАГАЗИНОВ ---")

        shops_list = list(self._active_mall.gallery.shops.values())
        if not shops_list:
            print("В этом ТЦ пока нет магазинов.")
        else:
            for idx, shop in enumerate(shops_list, 1):
                print(f"[{idx}] {shop.name} (Продавец: {shop.seller.name}, Рейтинг: {shop.seller.service_rating:.1f})")

        print("-" * 50)
        print("[q] Добавить магазин   [w] Удалить магазин")
        print("[0] Назад к списку ТЦ")

        choice = input("Выберите магазин (цифра) или действие (буква): ").strip().upper()

        if choice == '0':
            self._state = 0
        elif choice == 'Q' and self._on_add_shop:
            name = input("Название магазина: ").strip()
            seller = input("Имя продавца: ").strip()
            if name and seller: self._on_add_shop(name, seller)
        elif choice == 'W' and self._on_delete_shop:
            name = input("Название магазина для удаления: ").strip()
            self._on_delete_shop(name)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(shops_list):
                self._active_shop_name = shops_list[idx].name
                self._state = 2
            else:
                self.show_error("Неверный номер магазина.")

    def _render_products(self):
        print("\n" + "=" * 50)
        if not self._active_mall or not self._active_shop_name:
            self._state = 1
            return

        shop = self._active_mall.gallery.shops.get(self._active_shop_name)
        if not shop:
            self._state = 1
            return

        print(f"Магазин: {shop.name} (ТЦ: {self._active_mall.name})")
        print("--- ИНВЕНТАРЬ ---")

        if not shop.inventory:
            print("В магазине пока нет товаров.")
        else:
            for prod in shop.inventory.values():
                print(f"ID: {prod.id} | {prod.name} | Цена: ${prod.price:.2f} | Остаток: {prod.stock} шт.")

        print("-" * 50)
        print("[q] Купить товар       [w] Добавить товар")
        print("[e] Удалить товар      [r] Оценить магазин")
        print("[0] Назад к списку магазинов")

        choice = input("Выберите действие: ").strip().upper()

        if choice == '0':
            self._state = 1
        elif choice == 'Q' and self._on_purchase:
            p_id = input("Введите ID товара для покупки: ").strip()
            if p_id.isdigit():
                self._on_purchase(shop.name, int(p_id))
            else:
                self.show_error("ID должен быть числом.")
        elif choice == 'W' and self._on_add_product:
            try:
                p_id = int(input("ID товара: "))
                p_name = input("Название товара: ").strip()
                price = float(input("Цена ($): "))
                stock = int(input("Количество (шт): "))
                if p_name: self._on_add_product(shop.name, p_id, p_name, price, stock)
            except ValueError:
                self.show_error("Некорректный формат ввода.")
        elif choice == 'E' and self._on_delete_product:
            p_id = input("ID товара для удаления: ").strip()
            if p_id.isdigit():
                self._on_delete_product(shop.name, int(p_id))
            else:
                self.show_error("ID должен быть числом.")
        elif choice == 'R' and self._on_rate:
            try:
                rating = float(input("Ваша оценка (1.0 - 5.0): "))
                self._on_rate(shop.name, rating)
            except ValueError:
                self.show_error("Оценка должна быть числом.")

    # --- View Methods (Вызываются Presenter-ом) ---
    def show_message(self, msg: str):
        print(f"\nУСПЕХ {msg}")

    def show_error(self, err: str):
        print(f"\nОШИБКА {err}")

    def update_customer_info(self, c: Customer):
        self._customer_cache = c

    def refresh_all_data(self, malls: dict, active: ShoppingMall):
        self._malls_cache = malls
        self._active_mall = active

    def update_paged_view_shops(self, active_mall: ShoppingMall):
        """Синхронизация активного ТЦ с презентером."""
        self._active_mall = active_mall

    def show_search_results(self, results):
        print("\n--- РЕЗУЛЬТАТЫ ПОИСКА ---")
        if not results:
            print("Товары не найдены.")
        for s, p in results:
            print(f"- {s.name} | {p.name} (ID: {p.id}) | ${p.price:.2f} | {p.stock} шт.")

    def show_purchased_items(self, items):
        print("\n--- ВАШИ ПОКУПКИ ---")
        if not items:
            print("У вас пока нет покупок.")
        for i in items:
            print(f"- {i.name} (${i.price:.2f})")

    # --- Binds ---
    def bind_search(self, cb):
        self._on_search = cb

    def bind_purchase(self, cb):
        self._on_purchase = cb

    def bind_change_balance(self, cb):
        self._on_change_balance = cb

    def bind_select_mall(self, cb):
        self._on_select_mall = cb

    def bind_toggle_promotion(self, cb):
        self._on_toggle_promo = cb

    def bind_rate_service(self, cb):
        self._on_rate = cb

    def bind_view_purchases(self, cb):
        self._on_view_purchases = cb

    def bind_add_mall(self, cb):
        self._on_add_mall = cb

    def bind_delete_mall(self, cb):
        self._on_delete_mall = cb

    def bind_add_shop(self, cb):
        self._on_add_shop = cb

    def bind_delete_shop(self, cb):
        self._on_delete_shop = cb

    def bind_add_product(self, cb):
        self._on_add_product = cb

    def bind_delete_product(self, cb):
        self._on_delete_product = cb