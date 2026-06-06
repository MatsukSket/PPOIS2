from typing import List, Tuple
from domain.models import ShoppingMall, Shop, Product, Buyer
from domain.exceptions import ShopNotFoundError


class MallOperations:
    """
    Service class handling the main business operations of the mall.
    Make simple interactions with the domain model.
    """

    def __init__(self, mall: ShoppingMall) -> None:
        self.mall = mall

    def search_product(self, product_name: str) -> List[Tuple[Shop, Product]]:
        """
        Searches for a product by name across all shops in the gallery.
        Returns a list of tuples containing the shop and the matching product.
        """
        found_items = []
        for shop in self.mall.gallery.shops.values():
            for product in shop.inventory.values():
                if product_name.lower() in product.name.lower():
                    found_items.append((shop, product))
        return found_items

    def purchase_item(self, buyer: Buyer, shop_name: str, product_id: int) -> None:
        """
        Handles the purchase operation using the shop's cash register.
        """
        shop = self.mall.gallery.shops.get(shop_name)
        if not shop:
            raise ShopNotFoundError(f"Shop '{shop_name}' not found in the gallery.")

        product = shop.inventory.get(product_id)
        if not product:
            raise ValueError(f"Product ID {product_id} not found in '{shop_name}'.")

        # Delegate the transaction to the cash register
        shop.cash_register.process_purchase(buyer, product, shop.active_promotion)

    def toggle_promotion_participation(self, buyer: Buyer) -> None:
        """
        Enables or disables buyer's participation in mall/shop promotions.
        """
        buyer.participates_in_promotions = not buyer.participates_in_promotions

    def rent_shop_space(self, shop: Shop) -> None:
        """
        Operation for a new shop to rent space in the gallery.
        """
        self.mall.gallery.rent_space(shop)

    def rate_service(self, shop_name: str, rating: float) -> None:
        """
        Rates the service of a shop's seller.
        """
        if not (1.0 <= rating <= 5.0):
            raise ValueError("Rating must be between 1.0 and 5.0.")

        shop = self.mall.gallery.shops.get(shop_name)
        if not shop:
            raise ShopNotFoundError(f"Shop '{shop_name}' not found in the gallery.")

        shop.seller.update_rating(rating)