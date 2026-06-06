# main.py
from domain.models import (
    ShoppingMall, ShoppingGallery, Shop, Seller, Product, Buyer, Promotion
)
from services.operations import MallOperations
from cli.interface import CLI


def main() -> None:
    """
    Entry point of the Shopping Mall application.
    Initializes dummy data and starts the CLI.
    """
    # 1. Initialize the mall and gallery
    gallery = ShoppingGallery(capacity=5)
    mall = ShoppingMall(name="MegaCenter", gallery=gallery)

    # 2. Create sellers and shops
    tech_seller = Seller(name="Alice", service_rating=4.5, reviews_count=10)
    tech_shop = Shop(name="TechStore", seller=tech_seller)

    cloth_seller = Seller(name="Bob", service_rating=4.8, reviews_count=5)
    cloth_shop = Shop(name="FashionHub", seller=cloth_seller)

    # Add shops to the gallery
    mall.gallery.rent_space(tech_shop)
    mall.gallery.rent_space(cloth_shop)

    # 3. Add products to shops
    tech_shop.add_product(Product(id=101, name="Laptop", price=1200.0, stock=5))
    tech_shop.add_product(Product(id=102, name="Smartphone", price=800.0, stock=10))

    cloth_shop.add_product(Product(id=201, name="T-Shirt", price=25.0, stock=50))
    cloth_shop.add_product(Product(id=202, name="Jeans", price=60.0, stock=20))

    # Add a promotion to the tech shop
    tech_shop.active_promotion = Promotion(name="Black Friday", discount_percent=10.0)

    # 4. Create a buyer
    buyer = Buyer(name="John Doe", balance=1500.0)

    # 5. Initialize services and CLI
    operations = MallOperations(mall)
    cli = CLI(operations=operations, current_user=buyer)

    # Start the application
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\nApplication forcefully closed. Goodbye!")


if __name__ == "__main__":
    main()