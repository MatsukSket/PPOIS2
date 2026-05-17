class ShoppingMallException(Exception):
    """Базовое исключение для системы Торгового Центра."""
    pass

class OutOfStockError(ShoppingMallException):
    pass

class InsufficientFundsError(ShoppingMallException):
    pass

class ShopNotFoundError(ShoppingMallException):
    pass

class SpaceAlreadyRentedError(ShoppingMallException):
    pass