# tests/test_models.py
import unittest
from domain.models import Product, Buyer, Promotion, CashRegister
from domain.exceptions import OutOfStockError, InsufficientFundsError


class TestShoppingMallDomain(unittest.TestCase):
    """
    Unit tests for the core domain models and business logic.
    """

    def setUp(self) -> None:
        """Set up standard objects for testing."""
        self.product = Product(id=1, name="Test Item", price=100.0, stock=2)
        self.buyer = Buyer(name="Tester", balance=150.0)
        self.promotion = Promotion(name="10% Off", discount_percent=10.0)
        self.cash_register = CashRegister()

    def test_product_decrease_stock_success(self) -> None:
        """Test successful stock reduction."""
        self.product.decrease_stock(1)
        self.assertEqual(self.product.stock, 1)

    def test_product_decrease_stock_exception(self) -> None:
        """Test OutOfStockError when requesting too much."""
        with self.assertRaises(OutOfStockError):
            self.product.decrease_stock(5)

    def test_buyer_deduct_funds_success(self) -> None:
        """Test successful funds deduction."""
        self.buyer.deduct_funds(50.0)
        self.assertEqual(self.buyer.balance, 100.0)

    def test_buyer_deduct_funds_exception(self) -> None:
        """Test InsufficientFundsError when balance is too low."""
        with self.assertRaises(InsufficientFundsError):
            self.buyer.deduct_funds(200.0)

    def test_promotion_apply_discount(self) -> None:
        """Test that discount is calculated correctly."""
        discounted_price = self.promotion.apply_discount(100.0)
        self.assertEqual(discounted_price, 90.0)

    def test_cash_register_purchase_without_promo(self) -> None:
        """Test full purchase flow without promotion."""
        self.cash_register.process_purchase(self.buyer, self.product)
        self.assertEqual(self.buyer.balance, 50.0)
        self.assertEqual(self.product.stock, 1)
        self.assertEqual(len(self.buyer.purchased_items), 1)
        self.assertEqual(self.cash_register.total_revenue, 100.0)

    def test_cash_register_purchase_with_promo(self) -> None:
        """Test full purchase flow with an active promotion."""
        self.buyer.participates_in_promotions = True
        self.cash_register.process_purchase(self.buyer, self.product, self.promotion)

        # 100 - 10% = 90. Balance: 150 - 90 = 60
        self.assertEqual(self.buyer.balance, 60.0)
        self.assertEqual(self.cash_register.total_revenue, 90.0)


if __name__ == '__main__':
    unittest.main()