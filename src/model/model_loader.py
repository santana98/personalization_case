# src/model/model_loader.py
from datetime import datetime, UTC
import pickle
from pathlib import Path
from typing import Any

from src.core.logging import app_logger


logger = app_logger.getChild("model.model_loader")


class ModelLoaderError(RuntimeError):
    """Error related to loading the artifact."""


class _ModelRegistry:
    """
    Singleton registry loaded at application startup.
    """

    def __init__(self) -> None:
        self.model: Any | None = None
        self.scaler: Any | None = None
        self.feature_cols: list[str] | None = None
        self.loaded: bool = False
        self.model_loaded_at = datetime.now(UTC)

    def load(self, model_path: Path) -> None:
        if self.loaded:
            logger.debug("Model already loaded. Skipping new load.")
            return

        model_path = model_path

        logger.info(
            "Starting model load: %s",
            model_path,
        )

        if not model_path.exists():
            logger.error(
                "Model file not found: %s",
                model_path,
            )

            raise ModelLoaderError(f"Model not found: {model_path}")

        try:
            with model_path.open("rb") as f:
                artifact = pickle.load(f)

        except Exception as exc:
            logger.exception(
                "Error loading artifact: %s",
                model_path,
            )
            raise ModelLoaderError(
                f"FFailed to load artifact '{model_path}': {exc}"
            ) from exc

        if not isinstance(artifact, dict):
            raise ModelLoaderError("Invalid artifact. Expected dict.")

        required_keys = {
            "model",
            "scaler",
            "feature_cols",
        }

        missing = required_keys - artifact.keys()

        if missing:
            raise ModelLoaderError(
                f"Incomplete artifact. Missing keys: {sorted(missing)}"
            )

        self.model = artifact["model"]
        self.scaler = artifact["scaler"]
        self.feature_cols = list(artifact["feature_cols"])

        self.loaded = True

        logger.info("Model loaded successfully.")

    def validate_features(
        self,
        feature_names: list[str],
    ) -> bool:
        """
        Validates that the order of the received features
        exactly matches the one used during training.
        """

        if self.feature_cols is None:
            raise ModelLoaderError("Model not loaded yet.")

        return feature_names == self.feature_cols


_registry = _ModelRegistry()


def load_model(
    model_path: str,
) -> None:
    return _registry.load(Path(model_path))


def get_model() -> Any:
    if _registry.model is None:
        raise ModelLoaderError("Model not loaded.")

    return _registry.model


def get_scaler() -> Any:
    if _registry.scaler is None:
        raise ModelLoaderError("Scaler not loaded.")

    return _registry.scaler


def get_feature_cols() -> list[str]:
    if _registry.feature_cols is None:
        raise ModelLoaderError("Features not loaded.")

    return _registry.feature_cols


def validate_feature_order(
    feature_names: list[str],
) -> bool:
    return _registry.validate_features(feature_names)
