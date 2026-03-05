import unittest
from src.models import (
    Product, Customer, Seller, Shop,
    ShoppingGallery, ShoppingMall, Promotion
)
from src.services import MallServices
from src.exceptions import (
    OutOfStockError, InsufficientFundsError,
    SpaceAlreadyRentedError, ShopNotFoundError
)


class TestShoppingMall(unittest.TestCase):
    def setUp(self):
        """Prepare func."""
        self.gallery = ShoppingGallery(capacity=2)
        self.mall = ShoppingMall(name="TestMall", gallery=self.gallery)

        self.seller = Seller(name="TestSeller")
        self.shop = Shop(name="TestShop", seller=self.seller)
        self.mall.gallery.rent_space(self.shop)

        self.product = Product(id=1, name="TestPhone", price=1000.0, stock=2)
        self.shop.add_product(self.product)

        self.customer = Customer(name="TestUser", balance=1500.0)
        self.services = MallServices(self.mall)

    def test_product_decrease_stock(self):
        """Check if product decreases stock."""
        self.product.decrease_stock(1)
        self.assertEqual(self.product.stock, 1)

        with self.assertRaises(OutOfStockError):
            self.product.decrease_stock(5)

    def test_customer_deduct_funds(self):
        """Check if customer deduct funds."""
        self.customer.deduct_funds(500.0)
        self.assertEqual(self.customer.balance, 1000.0)

        with self.assertRaises(InsufficientFundsError):
            self.customer.deduct_funds(2000.0)

    def test_gallery_capacity_limit(self):
        """Check if gallery capacity limit."""
        shop2 = Shop(name="Shop2", seller=self.seller)
        shop3 = Shop(name="Shop3", seller=self.seller)

        self.mall.gallery.rent_space(shop2)  # Это должно сработать (вместимость 2)

        with self.assertRaises(SpaceAlreadyRentedError):
            self.mall.gallery.rent_space(shop3)  # Лимит превышен

    def test_successful_purchase(self):
        """Check if successful purchase."""
        self.services.purchase_item(self.customer, "TestShop", 1)

        self.assertEqual(self.customer.balance, 500.0)  # 1500 - 1000
        self.assertEqual(self.product.stock, 1)  # 2 - 1
        self.assertEqual(len(self.customer.purchased_items), 1)
        self.assertEqual(self.shop.cash_register.total_revenue, 1000.0)

    def test_purchase_with_promotion(self):
        """Check if successful purchase with promotion."""
        # 10% sale
        self.shop.active_promotion = Promotion(name="Sale 10%", discount_percent=10)
        self.customer.participates_in_promotions = True

        self.services.purchase_item(self.customer, "TestShop", 1)

        # Товар стоил 1000, со скидкой 10% должен стоить 900
        self.assertEqual(self.customer.balance, 600.0)  # 1500 - 900
        self.assertEqual(self.shop.cash_register.total_revenue, 900.0)

    def test_search_product(self):
        """Check if searching product."""
        # Ищем 'phone' с маленькой буквы, хотя товар называется 'TestPhone'
        results = self.services.search_product("phone")

        self.assertEqual(len(results), 1)
        shop, product = results[0]
        self.assertEqual(shop.name, "TestShop")
        self.assertEqual(product.name, "TestPhone")

    def test_rate_seller(self):
        """Check if rate seller."""
        self.services.rate_service("TestShop", 4.0)
        self.services.rate_service("TestShop", 5.0)

        # Среднее между 4.0 и 5.0 = 4.5
        self.assertEqual(self.seller.service_rating, 4.5)
        self.assertEqual(self.seller.reviews_count, 2)


if __name__ == '__main__':
    unittest.main()