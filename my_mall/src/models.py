from dataclasses import dataclass, field
from typing import List, Dict, Optional
from exceptions import (
    OutOfStockError,
    InsufficientFundsError,
    SpaceAlreadyRentedError
)
from copy import copy

@dataclass
class Product:
    """Product model."""
    id: int
    name: str
    price: float
    stock: int

    def decrease_stock(self, quantity: int = 1) -> None:
        if self.stock < quantity:
            raise OutOfStockError(f"Product '{self.name}' is out of stock.")
        self.stock -= quantity


@dataclass
class Promotion:
    """Promotion model"""
    name: str
    discount_percent: float

    def apply_discount(self, price: float) -> float:
        return price * (1 - self.discount_percent / 100)


@dataclass
class Person:
    """Person model."""
    name: str


@dataclass
class Customer(Person):
    """Customer model."""
    balance: float
    purchased_items: List[Product] = field(default_factory=list)
    participates_in_promotions: bool = False

    def deduct_funds(self, amount: float) -> None:
        if self.balance < amount:
            raise InsufficientFundsError(
                f"Not enough funds. Balance: {self.balance:.2f}, required: {amount:.2f}"
            )
        self.balance -= amount


@dataclass
class Seller(Person):
    """Seller model."""
    service_rating: float = 0.0
    reviews_count: int = 0

    def update_rating(self, new_rating: float) -> None:
        """Updating the rating based on the new score (from 1 to 5)"""
        total_score = self.service_rating * self.reviews_count + new_rating
        self.reviews_count += 1
        self.service_rating = total_score / self.reviews_count


class CashRegister:
    """Cash Register."""
    def __init__(self):
        self.total_revenue: float = 0.0

    def process_purchase(self, customer: Customer, product: Product, promotion: Optional[Promotion] = None) -> None:
        """Making purchase"""
        final_price = product.price

        if promotion and customer.participates_in_promotions:
            final_price = promotion.apply_discount(final_price)

        customer.deduct_funds(final_price)
        product.decrease_stock(1)
        purchased_item = copy(product)
        customer.purchased_items.append(purchased_item)
        self.total_revenue += final_price


@dataclass
class Shop:
    """Shop model."""
    name: str
    seller: Seller
    cash_register: CashRegister = field(default_factory=CashRegister)
    inventory: Dict[int, Product] = field(default_factory=dict)
    active_promotion: Optional[Promotion] = None

    def add_product(self, product: Product) -> None:
        self.inventory[product.id] = product


class ShoppingGallery:
    """Shopping Gallery."""
    def __init__(self, capacity: int = 10) -> None:
        self.capacity = capacity
        self.shops: Dict[str, Shop] = {}

    def rent_space(self, shop: Shop) -> None:
        if len(self.shops) >= self.capacity:
            raise SpaceAlreadyRentedError("There are no spaces available for rent in the gallery.")
        if shop.name in self.shops:
            raise SpaceAlreadyRentedError(f"Shop {shop.name} is already exists.")
        self.shops[shop.name] = shop


@dataclass
class ShoppingMall:
    """Shopping Mall model."""
    name: str
    gallery: ShoppingGallery = field(default_factory=ShoppingGallery)