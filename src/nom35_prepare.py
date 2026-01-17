from __future__ import annotations

import re
import unicodedata
import pandas as pd


def _normalize_str_or_na(x):
    if pd.isna(x):
        return pd.NA

    s = str(x).strip()
    if s == '' or s.lower() in ['nan', 'none', 'null', 'na', 'n/a']:
        return pd.NA

    return s


def _strip_accents(text):
    if pd.isna(text):
        return pd.NA

    s = str(text)
    s = ''.join([c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)])
    return s


def _only_letters_and_spaces(text):
    if pd.isna(text):
        return pd.NA

    s = str(text)
    s = re.sub(r'[^A-Za-z\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _proper_name(text):
    if pd.isna(text):
        return pd.NA

    s = str(text).strip()
    if s == '':
        return pd.NA

    return s.lower().title()


def _homologate_text_value(value):
    s = _normalize_str_or_na(value)
    if pd.isna(s):
        return pd.NA

    s = _strip_accents(s)
    s = _only_letters_and_spaces(s)
    s = _proper_name(s)

    return s


def _bin_numeric_series(
    series_in,
    step,
    start_value,
    no_spec_label = 'No especificado',
    min_value_allowed = None,
    include_zero_in_first_bin = False,
):
    """
    Crea bins tipo 'low-high'.

    Caso especial (lo que pidió el usuario):
    - Cuando include_zero_in_first_bin = True y start_value = 0:
      el primer bin es 0-step (incluye el 0 dentro del primer corte),
      y después se continúan bins de tamaño step:
        step = 2 -> 0-2, 3-4, 5-6, ...
        step = 3 -> 0-3, 4-6, 7-9, ...
        step = 4 -> 0-4, 5-8, 9-12, ...
        step = 6 -> 0-6, 7-12, 13-18, ...
        step = 12 -> 0-12, 13-24, 25-36, ...
    """
    s = pd.to_numeric(series_in, errors = 'coerce')

    if min_value_allowed is not None:
        s = s.where(s >= min_value_allowed, other = pd.NA)

    s_max = s.max(skipna = True)
    if pd.isna(s_max):
        return pd.Series([no_spec_label] * len(series_in), index = series_in.index)

    step = int(step)
    if step <= 0:
        return pd.Series([no_spec_label] * len(series_in), index = series_in.index)

    max_val = int(s_max)

    bins = []
    labels = []

    low = int(start_value)

    if include_zero_in_first_bin and int(start_value) == 0:
        high = int(start_value + step)      # primer corte: 0-step
    else:
        high = int(start_value + step - 1)  # corte normal: 0-(step-1)

    while low <= max_val:
        bins.append((low, high))
        labels.append(f'{low}-{high}')
        low = high + 1
        high = low + step - 1

    def _assign(v):
        if pd.isna(v):
            return no_spec_label

        try:
            vv = int(float(v))
        except Exception:
            return no_spec_label

        for (b_low, b_high), lab in zip(bins, labels):
            if b_low <= vv <= b_high:
                return lab

        if vv < bins[0][0]:
            return labels[0]

        return labels[-1]

    return s.map(_assign)


def _build_age_bins(series_age, step = 5, no_spec_label = 'No especificado'):
    """
    Bins de edad:
    - Si hay edades < 18, se etiquetan como '<18'
    - Siempre reserva 18-20
    - Después, desde 21:
        step = 5  -> 21-25, 26-30, ...
        step = 10 -> 21-30, 31-40, ...
    - NA se mantiene como 'No especificado'
    """
    age_num = pd.to_numeric(series_age, errors = 'coerce')
    age_num = age_num.where(age_num >= 0, other = pd.NA)

    out = pd.Series([no_spec_label] * len(age_num), index = age_num.index)

    # <18
    mask_lt_18 = age_num.between(0, 17, inclusive = 'both')
    out.loc[mask_lt_18] = '<18'

    # 18-20
    mask_18_20 = age_num.between(18, 20, inclusive = 'both')
    out.loc[mask_18_20] = '18-20'

    # >=21
    mask_21p = age_num >= 21
    if not mask_21p.any():
        return out

    step = int(step)
    if step <= 0:
        return out

    max_val = int(age_num[mask_21p].max(skipna = True))

    bins = []
    labels = []

    low = 21
    high = low + step - 1

    while low <= max_val:
        bins.append((low, high))
        labels.append(f'{low}-{high}')
        low = high + 1
        high = low + step - 1

    def _assign(v):
        if pd.isna(v):
            return no_spec_label

        try:
            vv = int(float(v))
        except Exception:
            return no_spec_label

        if vv < 21:
            return no_spec_label

        for (b_low, b_high), lab in zip(bins, labels):
            if b_low <= vv <= b_high:
                return lab

        return labels[-1]

    out.loc[mask_21p] = age_num.loc[mask_21p].map(_assign)
    return out


def _normalize_sexo(series_in):
    sexo_series = series_in.map(_normalize_str_or_na)

    def _norm(v):
        if pd.isna(v):
            return pd.NA

        s = str(v).strip().lower()

        if s in ['m', 'masc', 'masculino', 'hombre', 'varon', 'varón']:
            return 'Masculino'
        if s in ['f', 'fem', 'femenino', 'mujer']:
            return 'Femenino'

        return str(v).strip()

    return sexo_series.map(_norm)


def prepare_nom35_dataframe(df_in, edad_step = 5, antiguedad_step = 5):
    df = df_in.copy()

    cols_to_homologate = [
        'primer_nombre',
        'segundo_nombre',
        'primer_apellido',
        'segundo_apellido',
        'nombre_de_jefe_inmediato',
        'coloca_tu_puesto_actual',
        'area',
        'selecciona_el_tipo_de_posicion_que_tienes',
    ]

    for c in cols_to_homologate:
        if c in df.columns:
            df[c] = df[c].map(_homologate_text_value)

    if 'sexo' in df.columns:
        df['sexo_norm'] = _normalize_sexo(df['sexo']).fillna('No especificado')
    else:
        df['sexo_norm'] = 'No especificado'

    if 'edad' in df.columns:
        df['edad_num'] = pd.to_numeric(df['edad'], errors = 'coerce')
        df['rango_edad'] = _build_age_bins(df['edad_num'], step = int(edad_step)).fillna('No especificado')
    else:
        df['edad_num'] = pd.NA
        df['rango_edad'] = 'No especificado'

    if 'antiguedad_ano' in df.columns and 'antiguedad_meses' in df.columns:
        a = pd.to_numeric(df['antiguedad_ano'], errors = 'coerce')
        m = pd.to_numeric(df['antiguedad_meses'], errors = 'coerce')

        total_meses = a * 12 + m
        total_meses = total_meses.where(total_meses >= 0, other = pd.NA)

        df['antiguedad_total_meses'] = total_meses

        df['rango_antiguedad_meses'] = _bin_numeric_series(
            series_in = df['antiguedad_total_meses'],
            step = int(antiguedad_step),
            start_value = 0,
            no_spec_label = 'No especificado',
            min_value_allowed = 0,
            include_zero_in_first_bin = True,
        ).fillna('No especificado')
    else:
        df['antiguedad_total_meses'] = pd.NA
        df['rango_antiguedad_meses'] = 'No especificado'

    return df
