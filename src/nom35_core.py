from __future__ import annotations

import pandas as pd


REQUIRED_COLS = [
    'site',
    'count_final',
    'final',
]


def ensure_classified_layout(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            'Tus archivos no parecen estar en layout "clasificado". '
            f'Faltan columnas mínimas: {missing}. '
            'Sugerencia: sube el output tipo nom35_classified_df (con count_final, final, count_*).'
        )

    count_cols = [c for c in df.columns if c.startswith('count_')]
    if len(count_cols) == 0:
        raise ValueError(
            'No encontré columnas count_*. '
            'Sugerencia: sube el output tipo nom35_classified_df.'
        )

    return True
