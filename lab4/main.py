import sys
import os
import argparse
from PySide6.QtWidgets import QApplication

from src.models import ShoppingMall, ShoppingGallery, Shop, Seller, Product, Customer
from src.services import MallServices
from src.presenter import MainPresenter

from src.views.cli_view import CLIView
from src.views.gui_view import GUIView


def init_test_data(services: MallServices) -> Customer:
    """Создает стартовые данные только при первом запуске (если нет файла JSON)."""
    gallery = ShoppingGallery(capacity=5)
    mall = ShoppingMall(name="DanaMall", gallery=gallery)

    shop1 = Shop("ElectroSila", Seller("Nikita"))
    shop1.add_product(Product(101, "Laptop", 1200.0, 5))
    shop1.add_product(Product(102, "Phone", 800.0, 10))
    mall.gallery.rent_space(shop1)

    services.add_mall(mall)
    return Customer(name='Zakhar', balance=3000.0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['cli', 'gui'], default='gui', help="Режим запуска")
    args = parser.parse_args()

    services = MallServices()
    customer = Customer(name='Default', balance=0)  # Заглушка, перезапишется в Presenter

    # Если файла сохранения еще нет, генерируем базовые данные
    if not os.path.exists(MainPresenter.AUTO_SAVE_FILE):
        customer = init_test_data(services)

    app = None
    if args.mode == 'gui':
        app = QApplication.instance() or QApplication(sys.argv)
        view = GUIView()
    else:
        view = CLIView()

    # Presenter сам считает данные из JSON при инициализации
    presenter = MainPresenter(services, customer, view)

    try:
        presenter.run()
    except KeyboardInterrupt:
        print("\nЗавершение программы.")


if __name__ == '__main__':
    main()