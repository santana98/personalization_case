from typing import Any

import numpy as np
import pandas as pd

from src.model.model_loader import (
    get_feature_cols,
    get_model,
    get_scaler,
)


class PredictionError(RuntimeError):
    """Erro relacionado à inferência."""


def _validate_columns(
    columns: list[str],
    expected: list[str],
) -> None:
    """
    Exige correspondência exata entre
    features esperadas e recebidas.
    """

    received = set(columns)
    required = set(expected)

    missing = required - received
    extra = received - required

    if missing:
        raise PredictionError(
            f"Features ausentes: {sorted(missing)}"
        )

    if extra:
        raise PredictionError(
            f"Features não esperadas: {sorted(extra)}"
        )


def predict_score(
    features: dict[str, Any],
) -> float:
    """
    Realiza inferência para um único registro.

    Parameters
    ----------
    features:
        Dict contendo todas as features
        esperadas pelo modelo.

    Returns
    -------
    float
        Probabilidade da classe positiva.
    """

    expected_features = get_feature_cols()

    _validate_columns(
        list(features.keys()),
        expected_features,
    )

    df = pd.DataFrame([features])

    df = df[expected_features]

    scaler = get_scaler()
    model = get_model()

    x_scaled = scaler.transform(df.to_numpy())

    score = model.predict_proba(x_scaled)[0][1]

    return float(score)


def predict_scores(
    df_features: pd.DataFrame,
) -> np.ndarray:
    """
    Realiza inferência em lote.

    Parameters
    ----------
    df_features:
        DataFrame contendo apenas as
        features utilizadas pelo modelo.

    Returns
    -------
    np.ndarray
        Vetor de probabilidades.
    """

    expected_features = get_feature_cols()

    _validate_columns(
        df_features.columns.tolist(),
        expected_features,
    )

    df_ordered = df_features[
        expected_features
    ]

    scaler = get_scaler()
    model = get_model()

    x_scaled = scaler.transform(
        df_ordered.to_numpy()
    )

    probabilities = model.predict_proba(
        x_scaled
    )[:, 1]

    return probabilities