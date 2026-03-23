import pytest
from copy import copy

# Предполагается, что твой код лежит в модуле src
# Для работы тестов в одном файле без структуры папок просто импортируй классы
from src.models import (
    Product, Promotion, Customer, Seller, CashRegister,
    Shop, ShoppingGallery, ShoppingMall
)
from src.exceptions import (
    OutOfStockError, InsufficientFundsError,
    SpaceAlreadyRentedError, ShopNotFoundError
)
from src.services import MallServices


# --- Фикстуры (Fixtures) ---

@pytest.fixture
def sample_product():
    return Product(id=1, name="Smartphone", price=500.0, stock=2)


@pytest.fixture
def sample_promotion():
    return Promotion(name="BLACK FRIDAY", discount_percent=10.0)


@pytest.fixture
def sample_customer():
    return Customer(name="Alice", balance=1000.0)


@pytest.fixture
def sample_shop(sample_product):
    seller = Seller(name="Bob")
    shop = Shop(name="TechStore", seller=seller)
    shop.add_product(sample_product)
    return shop


@pytest.fixture
def mall_services(sample_shop):
    gallery = ShoppingGallery(capacity=2)
    mall = ShoppingMall(name="TestMall", gallery=gallery)
    services = MallServices(mall)
    services.rent_shop_space(sample_shop)
    return services


# --- Тесты для Моделей (Models) ---

def test_product_decrease_stock(sample_product):
    sample_product.decrease_stock(1)
    assert sample_product.stock == 1


def test_product_out_of_stock(sample_product):
    with pytest.raises(OutOfStockError):
        sample_product.decrease_stock(3)


def test_promotion_apply_discount(sample_promotion):
    price = 100.0
    discounted = sample_promotion.apply_discount(price)
    assert discounted == 90.0


def test_customer_deduct_funds(sample_customer):
    sample_customer.deduct_funds(200.0)
    assert sample_customer.balance == 800.0


def test_customer_insufficient_funds(sample_customer):
    with pytest.raises(InsufficientFundsError):
        sample_customer.deduct_funds(1500.0)


def test_seller_update_rating():
    seller = Seller(name="Test")
    seller.update_rating(5.0)
    seller.update_rating(3.0)
    assert seller.reviews_count == 2
    assert seller.service_rating == 4.0


def test_cash_register_process_purchase(sample_customer, sample_product):
    register = CashRegister()
    register.process_purchase(sample_customer, sample_product)

    assert sample_customer.balance == 500.0
    assert sample_product.stock == 1
    assert len(sample_customer.purchased_items) == 1
    assert register.total_revenue == 500.0


def test_shopping_gallery_rent_space(sample_shop):
    gallery = ShoppingGallery(capacity=1)
    gallery.rent_space(sample_shop)
    assert "TechStore" in gallery.shops

    # Проверка на превышение лимита
    shop2 = Shop(name="ExtraStore", seller=Seller(name="Charlie"))
    with pytest.raises(SpaceAlreadyRentedError):
        gallery.rent_space(shop2)


# --- Тесты для Сервисов (Services) ---

def test_search_product(mall_services):
    results = mall_services.search_product("smart")
    assert len(results) == 1
    shop, product = results[0]
    assert shop.name == "TechStore"
    assert product.name == "Smartphone"


def test_purchase_item_success(mall_services, sample_customer):
    mall_services.purchase_item(sample_customer, "TechStore", 1)
    assert sample_customer.balance == 500.0
    assert len(sample_customer.purchased_items) == 1


def test_purchase_item_shop_not_found(mall_services, sample_customer):
    with pytest.raises(ShopNotFoundError):
        mall_services.purchase_item(sample_customer, "GhostShop", 1)


def test_toggle_promotion(sample_customer):
    assert not sample_customer.participates_in_promotions
    MallServices.toggle_promotion_participation(sample_customer)
    assert sample_customer.participates_in_promotions


def test_rate_service(mall_services):
    mall_services.rate_service("TechStore", 4.0)
    shop = mall_services.mall.gallery.shops["TechStore"]
    assert shop.seller.service_rating == 4.0


def test_rate_service_invalid_rating(mall_services):
    with pytest.raises(ValueError):
        mall_services.rate_service("TechStore", 6.0)