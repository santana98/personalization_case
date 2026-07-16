from typing import Any

import numpy as np
import pandas as pd

from src.model.model_loader import (
    get_feature_cols,
    get_model,
    get_scaler,
)


class PredictionError(RuntimeError):
    """Error related to inference."""


def _validate_columns(
    columns: list[str],
    expected: list[str],
) -> None:
    """
    Requires an exact match between
    expected and received features.
    """

    received = set(columns)
    required = set(expected)

    missing = required - received
    extra = received - required

    if missing:
        raise PredictionError(f"Missing features: {sorted(missing)}")

    if extra:
        raise PredictionError(f"Unexpected features: {sorted(extra)}")


def predict_score(
    features: dict[str, Any],
) -> float:
    """
    Performs inference for a single record.

    Parameters
    ----------
    features:
        Dict containing all features
        expected by the model.

    Returns
    -------
    float
        Probability of the positive class.
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
    Performs batch inference.

    Parameters
    ----------
    df_features:
        DataFrame containing only the
        features used by the model.

    Returns
    -------
    np.ndarray
        Vector of probabilities.
    """

    expected_features = get_feature_cols()

    _validate_columns(
        df_features.columns.tolist(),
        expected_features,
    )

    df_ordered = df_features[expected_features]

    scaler = get_scaler()
    model = get_model()

    x_scaled = scaler.transform(df_ordered.to_numpy())

    probabilities = model.predict_proba(x_scaled)[:, 1]

    return probabilities
