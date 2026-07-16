import pandas as pd

from src.core.logging import app_logger
from src.features.exceptions import ProductNotFoundError
from src.features.domain import Product

logger = app_logger.getChild("features.product_processor")


class ProductProcessor:
    """
    Responsável por disponibilizar estruturas de consulta
    relacionadas ao catálogo de produtos.

    Estruturas geradas:

    - products_by_id
        Busca O(1) por product_id

    - popularity_ranking
        Lista de product_ids ordenados por popularity_score desc
    """

    def __init__(
        self,
        products_df: pd.DataFrame,
    ) -> None:
        logger.info(
            "Inicializando ProductProcessor. products=%d",
            len(products_df),
        )

        self._products_by_id = self._build_product_index(products_df)

        self._popularity_ranking = self._build_popularity_ranking(products_df)

        self._all_products = tuple(self._products_by_id.values())

        self._popular_products = self._build_popular_products()

        logger.info(
            "ProductProcessor inicializado. products=%d ranking=%d",
            len(self._products_by_id),
            len(self._popularity_ranking),
        )

    @staticmethod
    def _build_product_index(
        products_df: pd.DataFrame,
    ) -> dict[str, Product]:
        products: dict[str, Product] = {}

        for row in products_df.itertuples(index=False):
            products[row.product_id] = Product(
                product_id=row.product_id,
                category=row.category,
                price=row.price,
                avg_rating=row.avg_rating,
                popularity_score=row.popularity_score,
            )

        return products

    @staticmethod
    def _build_popularity_ranking(
        products_df: pd.DataFrame,
    ) -> list[str]:
        ranking = products_df.sort_values(
            by="popularity_score",
            ascending=False,
        )["product_id"].tolist()

        return ranking

    def _build_popular_products(
        self,
    ) -> tuple[Product, ...]:

        return tuple(
            sorted(
                self._all_products,
                key=lambda product: (
                    -product.popularity_score,
                    -product.avg_rating,
                    product.product_id,
                ),
            )
        )

    def get_product(
        self,
        product_id: str,
    ) -> Product:
        try:
            return self._products_by_id[product_id]

        except KeyError as exc:
            logger.error(
                "Produto desconhecido solicitado: %s",
                product_id,
            )

            raise ProductNotFoundError(f"Unknown product_id='{product_id}'") from exc

    def get_known_product_ids(
        self,
    ) -> set[str]:
        return set(self._products_by_id.keys())

    def get_popularity_ranking(
        self,
    ) -> list[str]:
        return self._popularity_ranking

    def get_all_products(
        self,
    ) -> tuple[Product, ...]:
        return self._all_products

    def get_popular_products(
        self,
    ) -> tuple[Product, ...]:
        return self._popular_products
