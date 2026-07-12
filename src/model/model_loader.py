# src/model/model_loader.py
from datetime import datetime, UTC
import os
import pickle
from pathlib import Path
from typing import Any

from src.core.logging import app_logger

DEFAULT_MODEL_PATH = Path("src/model/artifacts/model.pkl")

logger = app_logger.getChild('model_loader')

class ModelLoaderError(RuntimeError):
    """Erro relacionado ao carregamento do artefato."""


class _ModelRegistry:
    """
    Registry singleton carregado no startup da aplicação.
    """

    def __init__(self) -> None:
        self.model: Any | None = None
        self.scaler: Any | None = None
        self.feature_cols: list[str] | None = None
        self.loaded: bool = False
        self.model_loaded_at = datetime.now(UTC)

    def load(self) -> None:
        if self.loaded:
            logger.debug("Modelo já carregado. Ignorando novo carregamento.")
            return

        model_path = Path(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))

        logger.info(
            "Iniciando carregamento do modelo: %s",
            model_path,
        )

        if not model_path.exists():
            logger.error(
                "Arquivo de modelo não encontrado: %s",
                model_path,
            )

            raise ModelLoaderError(f"Modelo não encontrado: {model_path}")

        try:
            with model_path.open("rb") as f:
                artifact = pickle.load(f)

        except Exception as exc:
            logger.exception(
                "Erro ao carregar artefato: %s",
                model_path,
            )
            raise ModelLoaderError(
                f"Falha ao carregar artefato '{model_path}': {exc}"
            ) from exc

        if not isinstance(artifact, dict):
            raise ModelLoaderError("Artefato inválido. Esperado dict.")

        required_keys = {
            "model",
            "scaler",
            "feature_cols",
        }

        missing = required_keys - artifact.keys()

        if missing:
            raise ModelLoaderError(
                f"Artefato incompleto. Chaves ausentes: {sorted(missing)}"
            )

        self.model = artifact["model"]
        self.scaler = artifact["scaler"]
        self.feature_cols = list(artifact["feature_cols"])

        self.loaded = True

        logger.info(
            "Modelo carregado com sucesso."
        )

    def validate_features(
        self,
        feature_names: list[str],
    ) -> bool:
        """
        Valida se a ordem das features recebidas
        corresponde exatamente à usada no treinamento.
        """

        if self.feature_cols is None:
            raise ModelLoaderError("Modelo ainda não carregado.")

        return feature_names == self.feature_cols


_registry = _ModelRegistry()


def load_model() -> None:
    """
    Deve ser chamado durante o startup da API.
    """
    _registry.load()


def get_model() -> Any:
    if _registry.model is None:
        raise ModelLoaderError("Modelo não carregado.")

    return _registry.model


def get_scaler() -> Any:
    if _registry.scaler is None:
        raise ModelLoaderError("Scaler não carregado.")

    return _registry.scaler


def get_feature_cols() -> list[str]:
    if _registry.feature_cols is None:
        raise ModelLoaderError("Features não carregadas.")

    return _registry.feature_cols


def validate_feature_order(
    feature_names: list[str],
) -> bool:
    return _registry.validate_features(feature_names)
