class ShoppingMallException(Exception):
    """Base exception for all Shopping Mall errors."""
    pass

class OutOfStockError(ShoppingMallException):
    """Throw if the product is now available."""
    pass

class InsufficientFundsError(ShoppingMallException):
    """Throw if the buyer not have enough money."""
    pass

class ShopNotFoundError(ShoppingMallException):
    """Throw if the shop is not found in the shopping gallery."""
    pass

class SpaceAlreadyRentedError(ShoppingMallException):
    """Throw if the gallery space is already occupied by another store."""
    pass