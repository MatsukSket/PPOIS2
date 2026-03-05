import sys
from src.models import Customer
from src.exceptions import ShoppingMallException, OutOfStockError
from src.services import MallServices


class CLI:
    """Command Line Interface class."""

    def __init__(self, operations: MallServices, current_user: Customer) -> None:
        self.operations = operations
        self.user = current_user

    def display_main_menu(self) -> None:
        print("\n" + "=" * 30)
        print(f"Welcome, {self.user.name}! Balance: ${self.user.balance:.2f}")
        print("--- Shopping Mall CLI ---")
        print("1. Search for a product")
        print("2. Buy a product")
        print("3. Toggle promotion participation")
        print("4. Rate a seller service")
        print("5. View purchased items")
        print("0. Exit")
        print("=" * 30)

    def run(self) -> None:
        while True:
            self.display_main_menu()
            choice = input('Select an option: ')

            try:
                if choice == '1':
                    self._handle_search()
                elif choice == '2':
                    self._handle_purchase()
                elif choice == '3':
                    self._handle_promotions()
                elif choice == '4':
                    self._handle_rating()
                elif choice == '5':
                    self._handle_profile()
                elif choice == '0':
                    print('Thank you for shopping with us! Bye!')
                    sys.exit(0)
                else:
                    print("Invalid choice. Please enter a number from 0 to 5.")
            except ShoppingMallException as sme:
                print(f"\n{sme}")
            except ValueError as ve:
                print(f"\n{ve}")
            except Exception as ex:
                print(f"\n{ex}")

    def _handle_search(self) -> None:
        query = input("Enter product name to search: ").strip()
        results = self.operations.search_product(query)

        if not results:
            print("No products found.")
            return

        print("\nSearch Results:")
        for shop, product in results:
            print(f"- Shop: '{shop.name}' | Product: '{product.name}' (ID: {product.id}) "
                  f"| Price: ${product.price:.2f} | Stock: {product.stock}")

    def _handle_purchase(self) -> None:
        shop_name = input("Enter the exact name of the shop: ").strip()
        product_id_str = input("Enter the Product ID you want to buy: ").strip()

        if not product_id_str.isdigit():
            raise ValueError("Product ID must be an integer.")

        self.operations.purchase_item(self.user, shop_name, int(product_id_str))
        print("\nPurchase successful! The item has been added to your inventory.")

    def _handle_promotions(self) -> None:
        self.operations.toggle_promotion_participation(self.user)
        status = "ENABLED" if self.user.participates_in_promotions else "DISABLED"
        print(f"\nPromotion participation is now {status}.")

    def _handle_rating(self) -> None:
        shop_name = input("Enter the shop name to rate: ").strip()
        rating_str = input("Enter your rating (1.0 to 5.0): ").strip()

        rating = float(rating_str)
        self.operations.rate_service(shop_name, rating)
        print(f"\nThank you! You rated '{shop_name}' with {rating} stars.")

    def _handle_profile(self) -> None:
        print(f"\nPurchased Items ({len(self.user.purchased_items)} total):")
        for item in self.user.purchased_items:
            print(f"- {item.name} (Original Price: ${item.price:.2f})")


