from src.models import ShoppingMall, ShoppingGallery, Shop, Customer, Product
from typing import List, Tuple
from src.exceptions import ShopNotFoundError


class MallServices:
    """Class to manage main buisness operations of the mall."""
    def __init__(self, mall: ShoppingMall) -> None:
        self.mall = mall

    def search_product(self, product_name: str) -> List[Tuple[Shop, Product]]:
        """Search for product by name in all shops in the gallery."""
        found_items = []
        for shop in self.mall.gallery.shops.values():
            for product in shop.inventory.values():
                if product_name.lower() in product.name.lower():
                    found_items.append((shop, product))

        return found_items

    def purchase_item(self, customer: Customer, shop_name: str, product_id: int)-> None:
        """Purchase operation."""
        shop = self.mall.gallery.shops.get(shop_name)
        if not shop:
            raise ShopNotFoundError(f'Shop {shop_name} not found.')

        product = shop.inventory.get(product_id)
        if not product:
            raise ValueError(f'Product with id {product_id} not found.')

        shop.cash_register.process_purchase(customer, product, shop.active_promotion)

    @staticmethod
    def toggle_promotion_participation(customer: Customer) -> None:
        customer.participates_in_promotions = not customer.participates_in_promotions

    def rent_shop_space(self, shop: Shop) -> None:
        self.mall.gallery.rent_space(shop)

    def rate_service(self, shop_name: str, rating: float) -> None:
        if not (1.0 <= rating <= 5.0):
            raise ValueError(f'Invalid rating {rating}. Rating must be vetween 1.0 and 5.0')

        shop = self.mall.gallery.shops.get(shop_name)
        if not shop:
            raise ShopNotFoundError(f'Shop {shop_name} not found.')

        shop.seller.update_rating(rating)





