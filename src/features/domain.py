from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Product:
    product_id: str
    category: str
    price: float
    avg_rating: float
    popularity_score: float


@dataclass(frozen=True, slots=True)
class Recommendation:
    product_id: str
    score: float
