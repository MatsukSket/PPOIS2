import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QMenuBar, QMessageBox, QTreeWidget, QTableWidget,
    QTableWidgetItem, QTreeWidgetItem, QPushButton, QLabel, QInputDialog, QListWidget, QHeaderView
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from src.models import Customer, ShoppingMall


class GUIView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Торговый Центр - Система Управления")
        self.resize(1000, 600)

        self._active_mall = None

        # Binds
        self._on_search = self._on_purchase = self._on_toggle_promo = self._on_rate = self._on_view_purchases = None
        self._on_change_balance = self._on_select_mall = None
        self._on_add_mall = self._on_delete_mall = self._on_add_shop = self._on_delete_shop = None
        self._on_add_product = self._on_delete_product = None

        self._init_ui()
        self._create_menu()

    def _init_ui(self):
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        self.lbl_user = QLabel("Загрузка...")
        self.lbl_user.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")

        # === 1. Древовидный вид (Tree View) ===
        self.tree_widget = QWidget()
        tree_layout = QVBoxLayout(self.tree_widget)
        tree_layout.addWidget(self.lbl_user)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Название", "Тип", "ID", "Цена", "Остаток"])
        self.tree.setColumnWidth(0, 250)
        self.tree.currentItemChanged.connect(self._ui_tree_selection_changed)
        tree_layout.addWidget(self.tree)

        btn_buy = QPushButton("Купить выбранное")
        btn_buy.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        btn_buy.clicked.connect(self._ui_buy_selected)
        tree_layout.addWidget(btn_buy)

        # === 2. Страничный вид (Stacked / Paged View) ===
        self.page_widget = QWidget()
        page_layout = QVBoxLayout(self.page_widget)
        page_layout.addWidget(self.lbl_user)

        self.nav_stack = QStackedWidget()
        page_layout.addWidget(self.nav_stack)

        # Страница 2.1: Список ТЦ (Индекс 0)
        self.page_malls = QWidget()
        malls_layout = QVBoxLayout(self.page_malls)
        malls_layout.addWidget(QLabel("Выберите Торговый Центр (Двойной клик для входа):"))
        self.list_malls = QListWidget()
        self.list_malls.itemDoubleClicked.connect(self._ui_open_mall)
        malls_layout.addWidget(self.list_malls)
        self.nav_stack.addWidget(self.page_malls)

        # Страница 2.2: Список магазинов внутри ТЦ (Индекс 1)
        self.page_shops = QWidget()
        shops_layout = QVBoxLayout(self.page_shops)

        nav_malls = QHBoxLayout()
        btn_back_malls = QPushButton("<- Назад к списку ТЦ")
        btn_back_malls.clicked.connect(lambda: self.nav_stack.setCurrentIndex(0))
        nav_malls.addWidget(btn_back_malls)

        self.lbl_current_mall = QLabel("ТЦ: ...")
        nav_malls.addWidget(self.lbl_current_mall)
        nav_malls.addStretch()
        shops_layout.addLayout(nav_malls)

        shops_layout.addWidget(QLabel("Выберите магазин (Двойной клик для входа):"))
        self.list_shops = QListWidget()
        self.list_shops.itemDoubleClicked.connect(self._ui_open_shop)
        shops_layout.addWidget(self.list_shops)
        self.nav_stack.addWidget(self.page_shops)

        # Страница 2.3: Внутри магазина (Таблица товаров) (Индекс 2)
        self.page_products = QWidget()
        prods_layout = QVBoxLayout(self.page_products)

        nav_shops = QHBoxLayout()
        btn_back_shops = QPushButton("<- Назад к магазинам")
        btn_back_shops.clicked.connect(lambda: self.nav_stack.setCurrentIndex(1))
        nav_shops.addWidget(btn_back_shops)

        self.lbl_current_shop = QLabel("Магазин: ...")
        nav_shops.addWidget(self.lbl_current_shop)
        nav_shops.addStretch()
        prods_layout.addLayout(nav_shops)

        self.table_prods = QTableWidget(0, 5)
        self.table_prods.setHorizontalHeaderLabels(["ID", "Название", "Цена", "Остаток", "Действие"])
        self.table_prods.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        prods_layout.addWidget(self.table_prods)
        self.nav_stack.addWidget(self.page_products)

        self.central_stack.addWidget(self.tree_widget)
        self.central_stack.addWidget(self.page_widget)

    def _create_menu(self):
        menu_bar = self.menuBar()

        crud_menu = menu_bar.addMenu("Управление")
        crud_menu.addAction("Добавить ТЦ", self._ui_add_mall)
        crud_menu.addAction("Удалить ТЦ", self._ui_del_mall)
        crud_menu.addSeparator()
        crud_menu.addAction("Добавить Магазин", self._ui_add_shop)
        crud_menu.addAction("Удалить Магазин", self._ui_del_shop)
        crud_menu.addSeparator()
        crud_menu.addAction("Добавить Товар", self._ui_add_product)
        crud_menu.addAction("Удалить Товар", self._ui_del_product)

        view_menu = menu_bar.addMenu("Вид")
        view_menu.addAction("Древовидный интерфейс", lambda: self.central_stack.setCurrentIndex(0))
        view_menu.addAction("Страничный интерфейс", lambda: self.central_stack.setCurrentIndex(1))

        acts_menu = menu_bar.addMenu("Действия")
        acts_menu.addAction("Изменить баланс", self._ui_change_balance)
        acts_menu.addAction("Мои покупки", lambda: self._on_view_purchases() if self._on_view_purchases else None)
        acts_menu.addAction("Оценить магазин", self._ui_rate_shop)

    # --- UI Helpers ---
    def _ui_tree_selection_changed(self, current, previous):
        if not current: return
        curr = current
        while curr.parent():
            curr = curr.parent()
        mall_name = curr.text(0)

        if self._on_select_mall:
            self._on_select_mall(mall_name)

    def update_paged_view_shops(self, active_mall: ShoppingMall):
        self._active_mall = active_mall
        self.list_shops.clear()
        if active_mall:
            self.lbl_current_mall.setText(f"ТЦ: {active_mall.name}")
            for s_name in active_mall.gallery.shops.keys():
                self.list_shops.addItem(s_name)

    def _ui_open_mall(self, item):
        mall_name = item.text()
        if self._on_select_mall:
            self._on_select_mall(mall_name)
        self.lbl_current_mall.setText(f"ТЦ: {mall_name}")
        self.nav_stack.setCurrentIndex(1)  # Переход к списку магазинов

    def _ui_open_shop(self, item):
        shop_name = item.text()
        self.lbl_current_shop.setText(f"Магазин: {shop_name}")
        shop = self._active_mall.gallery.shops.get(shop_name)
        if not shop: return

        self.table_prods.setRowCount(len(shop.inventory))
        for row, prod in enumerate(shop.inventory.values()):
            self.table_prods.setItem(row, 0, QTableWidgetItem(str(prod.id)))
            self.table_prods.setItem(row, 1, QTableWidgetItem(prod.name))
            self.table_prods.setItem(row, 2, QTableWidgetItem(f"${prod.price:.2f}"))
            self.table_prods.setItem(row, 3, QTableWidgetItem(str(prod.stock)))

            btn_buy = QPushButton("Купить")
            btn_buy.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
            btn_buy.clicked.connect(
                lambda checked, s=shop_name, pid=prod.id: self._on_purchase(s, pid) if self._on_purchase else None)
            self.table_prods.setCellWidget(row, 4, btn_buy)

        self.nav_stack.setCurrentIndex(2)  # Переход к таблице товаров

    def _ui_change_balance(self):
        amount, ok = QInputDialog.getDouble(self, "Баланс", "Введите новый баланс ($):", minValue=0.0,
                                            maxValue=999999.0, decimals=2)
        if ok and self._on_change_balance:
            self._on_change_balance(amount)

    def _ui_add_mall(self):
        name, ok = QInputDialog.getText(self, "ТЦ", "Название нового ТЦ:")
        if not ok or not name.strip(): return

        cap, ok = QInputDialog.getInt(self, "ТЦ", "Вместимость галереи (кол-во магазинов):", value=10, minValue=1)
        if ok and self._on_add_mall:
            self._on_add_mall(name.strip(), cap)

    def _ui_del_mall(self):
        item = self.tree.currentItem()
        if not item or item.text(1) != "ТЦ":
            self.show_error("Сначала выделите Торговый Центр в дереве!")
            return

        confirm = QMessageBox.question(self, "Удаление", f"Удалить ТЦ '{item.text(0)}' со всеми магазинами?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes and self._on_delete_mall:
            self._on_delete_mall(item.text(0))

    def _ui_buy_selected(self):
        item = self.tree.currentItem()
        if not item or item.text(1) != "Товар":
            self.show_error("Сначала выделите Товар в дереве!")
            return
        shop_name = item.parent().text(0)
        p_id = int(item.text(2))
        if self._on_purchase: self._on_purchase(shop_name, p_id)

    def _ui_add_shop(self):
        name, ok = QInputDialog.getText(self, "Магазин", "Название магазина:")
        if not ok or not name.strip(): return

        seller, ok = QInputDialog.getText(self, "Магазин", "Имя продавца:")
        if ok and seller.strip() and self._on_add_shop:
            self._on_add_shop(name.strip(), seller.strip())

    def _ui_del_shop(self):
        item = self.tree.currentItem()
        if not item or item.text(1) != "Магазин":
            self.show_error("Сначала выделите Магазин в дереве!")
            return
        if self._on_delete_shop: self._on_delete_shop(item.text(0))

    def _ui_add_product(self):
        item = self.tree.currentItem()
        if not item or item.text(1) != "Магазин":
            self.show_error("Сначала выделите магазин в дереве!")
            return
        shop_name = item.text(0)

        p_id, ok = QInputDialog.getInt(self, "Товар", "ID товара:")
        if not ok: return

        p_name, ok = QInputDialog.getText(self, "Товар", "Название товара:")
        if not ok or not p_name.strip(): return

        price, ok = QInputDialog.getDouble(self, "Товар", "Цена ($):", minValue=0.01, decimals=2)
        if not ok: return

        stock, ok = QInputDialog.getInt(self, "Товар", "Количество (шт):", minValue=1)
        if not ok: return

        if self._on_add_product:
            self._on_add_product(shop_name, p_id, p_name.strip(), price, stock)

    def _ui_del_product(self):
        item = self.tree.currentItem()
        if not item or item.text(1) != "Товар":
            self.show_error("Сначала выделите Товар в дереве!")
            return
        shop_name = item.parent().text(0)
        p_id = int(item.text(2))
        if self._on_delete_product: self._on_delete_product(shop_name, p_id)

    def _ui_rate_shop(self):
        s_name, ok = QInputDialog.getText(self, "Оценка", "Введите название магазина:")
        if not ok or not s_name.strip(): return

        rating, ok = QInputDialog.getDouble(self, "Оценка", "Оценка (1.0-5.0):", 5.0, 1.0, 5.0, 1)
        if ok and self._on_rate:
            self._on_rate(s_name.strip(), rating)

    # --- View Methods ---
    def start(self) -> None:
        self.show()
        sys.exit(QApplication.instance().exec())

    def show_message(self, msg: str):
        QMessageBox.information(self, "Успех", msg)

    def show_error(self, err: str):
        QMessageBox.warning(self, "Ошибка", err)

    def update_customer_info(self, c: Customer):
        self.lbl_user.setText(f"Пользователь: {c.name} | Баланс: ${c.balance:.2f}")

    def show_purchased_items(self, items):
        msg = "\n".join([f"- {i.name} (${i.price:.2f})" for i in items]) if items else "У вас пока нет покупок."
        QMessageBox.information(self, "Ваши покупки", msg)

    def show_search_results(self, results):
        pass

    def refresh_all_data(self, malls: dict, active: ShoppingMall):
        self._active_mall = active
        self.tree.blockSignals(True)
        self.tree.clear()
        self.list_malls.clear()
        self.list_shops.clear()

        if not malls:
            self.tree.blockSignals(False)
            return

        for mall in malls.values():
            # Дерево
            mall_node = QTreeWidgetItem([mall.name, "ТЦ", "", "", f"Мест: {mall.gallery.capacity}"])
            self.tree.addTopLevelItem(mall_node)

            # Страница: Список ТЦ
            self.list_malls.addItem(mall.name)

            for s_name, shop in mall.gallery.shops.items():
                shop_node = QTreeWidgetItem([s_name, "Магазин", "", "", f"Продавец: {shop.seller.name}"])
                mall_node.addChild(shop_node)
                for p_id, prod in shop.inventory.items():
                    shop_node.addChild(
                        QTreeWidgetItem([prod.name, "Товар", str(p_id), f"${prod.price:.2f}", str(prod.stock)]))

        self.tree.expandAll()
        self.tree.blockSignals(False)

        if active:
            self.lbl_current_mall.setText(f"ТЦ: {active.name}")
            for s_name in active.gallery.shops.keys():
                self.list_shops.addItem(s_name)

        curr_shop_text = self.lbl_current_shop.text().replace("Магазин: ", "")
        if curr_shop_text and self.nav_stack.currentIndex() == 2:
            mock_item = self.list_shops.findItems(curr_shop_text, Qt.MatchExactly)
            if mock_item: self._ui_open_shop(mock_item[0])

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