class DatasetValidationError(Exception):
    """Gerado quando um dataset não está em conformidade com o esquema esperado."""


class FeaturesError(Exception):
    """Base exception for recommendation domain."""


class ProductNotFoundError(FeaturesError):
    def __init__(self, product_id: str):
        self.product_id = product_id

        super().__init__(f"Product '{product_id}' not found.")


class UserAffinityNotFoundError(FeaturesError):
    def __init__(self, user_id: str):
        self.user_id = user_id

        super().__init__(f"Affinity not found for user '{user_id}'.")
