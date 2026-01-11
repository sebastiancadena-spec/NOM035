from __future__ import annotations

import pandas as pd
from src.nom35_scoring import ensure_or_classify


def ensure_classified_layout(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compat:
    - Si ya está clasificado, regresa el DF tal cual.
    - Si viene RAW, lo clasifica (scores + counts + final).
    """
    return ensure_or_classify(df)
