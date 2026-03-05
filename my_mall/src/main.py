from src.models import (
    ShoppingMall, ShoppingGallery,
    Shop, Seller, Product, Customer, Promotion
)
from src.services import MallServices
from src.cli import CLI


def main() -> None:
    # initialize the mall and gallery
    dana_gallery = ShoppingGallery(capacity=5)
    danamall = ShoppingMall(name="DanaMall", gallery=dana_gallery)

    # create sellers and shops
    tech_seller = Seller(name="Nikita", service_rating=4.5, reviews_count=14)
    tech_shop = Shop(name="ElectroSila", seller=tech_seller)

    cloth_seller = Seller(name="Alina", service_rating=3.0, reviews_count=4)
    cloth_shop = Shop("ZARA", cloth_seller)

    danamall.gallery.rent_space(tech_shop)
    danamall.gallery.rent_space(cloth_shop)

    # add the products to shops
    tech_shop.add_product(Product(id=101, name="Laptop", price=1200.0, stock=5))
    tech_shop.add_product(Product(id=102, name="Phone", price=800.0, stock=10))

    cloth_shop.add_product(Product(id=201, name="Shirt", price=25.0, stock=50))
    cloth_shop.add_product(Product(id=202, name="Jeans", price=60.0, stock=20))

    tech_shop.active_promotion = Promotion(name="MEGAA SALE", discount_percent=5)

    customer = Customer(name='Zakhar', balance = 1000)

    operations = MallServices(danamall)
    cli = CLI(operations, customer)

    try:
        cli.run()
    except KeyboardInterrupt:
        print("\nApplication forcefully closed. Goodbye!")


if __name__ == '__main__':
    main()
