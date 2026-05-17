import json
import os
from typing import List, Tuple, Dict, Optional
from src.models import ShoppingMall, ShoppingGallery, Shop, Customer, Product, Seller, Promotion
from src.exceptions import ShopNotFoundError, ShoppingMallException


class MallServices:
    def __init__(self) -> None:
        self.malls: Dict[str, ShoppingMall] = {}
        self.active_mall: Optional[ShoppingMall] = None

    def search_product(self, product_name: str) -> List[Tuple[Shop, Product]]:
        found_items = []
        if not self.active_mall: return found_items
        for shop in self.active_mall.gallery.shops.values():
            for product in shop.inventory.values():
                if product_name.lower() in product.name.lower():
                    found_items.append((shop, product))
        return found_items

    def purchase_item(self, customer: Customer, shop_name: str, product_id: int) -> None:
        if not self.active_mall: raise ShoppingMallException("ТЦ не выбран.")
        shop = self.active_mall.gallery.shops.get(shop_name)
        if not shop: raise ShopNotFoundError(f"Магазин {shop_name} не найден.")
        product = shop.inventory.get(product_id)
        if not product: raise ValueError(f"Товар с ID {product_id} не найден.")
        shop.cash_register.process_purchase(customer, product, shop.active_promotion)

    @staticmethod
    def toggle_promotion_participation(customer: Customer) -> None:
        customer.participates_in_promotions = not customer.participates_in_promotions

    def rate_service(self, shop_name: str, rating: float) -> None:
        if not self.active_mall: raise ShoppingMallException("ТЦ не выбран.")
        shop = self.active_mall.gallery.shops.get(shop_name)
        if not shop: raise ShopNotFoundError(f"Магазин {shop_name} не найден.")
        shop.seller.update_rating(rating)

    # --- CRUD ОПЕРАЦИИ ---
    def add_mall(self, mall: ShoppingMall) -> None:
        self.malls[mall.name] = mall
        if not self.active_mall: self.active_mall = mall

    def remove_mall(self, mall_name: str) -> None:
        if mall_name in self.malls:
            del self.malls[mall_name]
            if self.active_mall and self.active_mall.name == mall_name:
                self.active_mall = next(iter(self.malls.values())) if self.malls else None

    def add_shop_to_active_gallery(self, shop: Shop) -> None:
        if not self.active_mall: raise ShoppingMallException("ТЦ не выбран.")
        self.active_mall.gallery.rent_space(shop)

    def remove_shop_from_active_gallery(self, shop_name: str) -> None:
        if not self.active_mall: raise ShoppingMallException("ТЦ не выбран.")
        if shop_name in self.active_mall.gallery.shops:
            del self.active_mall.gallery.shops[shop_name]

    def add_product_to_shop(self, shop_name: str, product: Product) -> None:
        if not self.active_mall: raise ShoppingMallException("ТЦ не выбран.")

        # ГЛОБАЛЬНАЯ ПРОВЕРКА НА УНИКАЛЬНОСТЬ ID ВО ВСЕХ ТЦ И МАГАЗИНАХ
        for mall in self.malls.values():
            for s in mall.gallery.shops.values():
                if product.id in s.inventory:
                    raise ValueError(
                        f"Товар с ID {product.id} уже существует в магазине '{s.name}' (ТЦ '{mall.name}')!")

        shop = self.active_mall.gallery.shops.get(shop_name)
        if not shop: raise ShopNotFoundError(f"Магазин '{shop_name}' не найден.")

        shop.add_product(product)

    def remove_product_from_shop(self, shop_name: str, product_id: int) -> None:
        if not self.active_mall: raise ShoppingMallException("ТЦ не выбран.")
        shop = self.active_mall.gallery.shops.get(shop_name)
        if shop and product_id in shop.inventory:
            del shop.inventory[product_id]

    # --- JSON Сериализация (Автосохранение) ---
    def save_to_json(self, filepath: str, customer: Customer) -> None:
        data = {
            "customer": {
                "name": customer.name, "balance": customer.balance,
                "participates_in_promotions": customer.participates_in_promotions,
                "purchased_items": [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock} for p in
                                    customer.purchased_items]
            },
            "malls": []
        }
        for mall in self.malls.values():
            m_data = {"name": mall.name, "capacity": mall.gallery.capacity, "shops": []}
            for shop in mall.gallery.shops.values():
                s_data = {
                    "name": shop.name,
                    "seller": {"name": shop.seller.name, "rating": shop.seller.service_rating,
                               "reviews": shop.seller.reviews_count},
                    "revenue": shop.cash_register.total_revenue,
                    "inventory": [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock} for p in
                                  shop.inventory.values()],
                    "promotion": {"name": shop.active_promotion.name,
                                  "discount": shop.active_promotion.discount_percent} if shop.active_promotion else None
                }
                m_data["shops"].append(s_data)
            data["malls"].append(m_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_from_json(self, filepath: str) -> Customer:
        if not os.path.exists(filepath):
            raise FileNotFoundError("Файл сохранения не найден.")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        c_data = data.get("customer", {})
        customer = Customer(name=c_data.get("name", "Unknown"), balance=c_data.get("balance", 0.0))
        customer.participates_in_promotions = c_data.get("participates_in_promotions", False)
        for item in c_data.get("purchased_items", []):
            customer.purchased_items.append(Product(item["id"], item["name"], item["price"], item["stock"]))

        self.malls.clear()
        self.active_mall = None
        for m_data in data.get("malls", []):
            mall = ShoppingMall(m_data["name"], ShoppingGallery(m_data.get("capacity", 10)))
            for s_data in m_data.get("shops", []):
                seller = Seller(s_data["seller"]["name"], s_data["seller"]["rating"], s_data["seller"]["reviews"])
                shop = Shop(s_data["name"], seller)
                shop.cash_register.total_revenue = s_data.get("revenue", 0.0)
                for p_data in s_data.get("inventory", []):
                    shop.add_product(Product(p_data["id"], p_data["name"], p_data["price"], p_data["stock"]))
                if s_data.get("promotion"):
                    shop.active_promotion = Promotion(s_data["promotion"]["name"], s_data["promotion"]["discount"])
                mall.gallery.rent_space(shop)
            self.add_mall(mall)
        if self.malls: self.active_mall = list(self.malls.values())[0]
        return customer