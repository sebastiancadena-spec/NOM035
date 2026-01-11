from __future__ import annotations

import pandas as pd


# 10. Diccionarios de umbrales (categorías, dominios y final)

TH_CAT = {
    'ambiente_de_trabajo': {
        'nulo o despreciable': 0,
        'bajo': 5,
        'medio': 9,
        'alto': 11,
        'muy alto': 14,
    },
    'factores_propios_de_la_actividad': {
        'nulo o despreciable': 0,
        'bajo': 15,
        'medio': 30,
        'alto': 45,
        'muy alto': 60,
    },
    'organizacion_en_el_trabajo': {
        'nulo o despreciable': 0,
        'bajo': 5,
        'medio': 7,
        'alto': 10,
        'muy alto': 13,
    },
    'liderazgo_y_relaciones_en_el_trabajo': {
        'nulo o despreciable': 0,
        'bajo': 14,
        'medio': 29,
        'alto': 42,
        'muy alto': 58,
    },
    'entorno_organizacional': {
        'nulo o despreciable': 0,
        'bajo': 10,
        'medio': 14,
        'alto': 18,
        'muy alto': 23,
    },
    'condiciones_deficientes_e_insalubres': {
        'nulo o despreciable': 0,
        'bajo': 1,
        'medio': 2,
        'alto': 3,
        'muy alto': 4,
    },
    'trabajos_peligrosos': {
        'nulo o despreciable': 0,
        'bajo': 1,
        'medio': 2,
        'alto': 3,
        'muy alto': 4,
    },
}

TH_DOM = {
    'condiciones_en_el_ambiente_de_trabajo': {
        'nulo o despreciable': 0,
        'bajo': 5,
        'medio': 9,
        'alto': 11,
        'muy alto': 14,
    },
    'carga_de_trabajo': {
        'nulo o despreciable': 0,
        'bajo': 15,
        'medio': 21,
        'alto': 27,
        'muy alto': 37,
    },
    'falta_de_control_sobre_el_trabajo': {
        'nulo o despreciable': 0,
        'bajo': 11,
        'medio': 16,
        'alto': 21,
        'muy alto': 25,
    },
    'jornada_de_trabajo': {
        'nulo o despreciable': 0,
        'bajo': 1,
        'medio': 2,
        'alto': 4,
        'muy alto': 6,
    },
    'influencia_en_la_relacion_trabajo_y_familia': {
        'nulo o despreciable': 0,
        'bajo': 4,
        'medio': 6,
        'alto': 8,
        'muy alto': 10,
    },
    'liderazgo': {
        'nulo o despreciable': 0,
        'bajo': 9,
        'medio': 12,
        'alto': 16,
        'muy alto': 20,
    },
    'relaciones_en_el_trabajo': {
        'nulo o despreciable': 0,
        'bajo': 10,
        'medio': 13,
        'alto': 17,
        'muy alto': 21,
    },
    'violencia': {
        'nulo o despreciable': 0,
        'bajo': 7,
        'medio': 10,
        'alto': 13,
        'muy alto': 16,
    },
    'reconocimiento_del_desempeno': {
        'nulo o despreciable': 0,
        'bajo': 6,
        'medio': 10,
        'alto': 14,
        'muy alto': 18,
    },
    'insuficiente_sentido_de_pertenencia_e_inestabilidad': {
        'nulo o despreciable': 0,
        'bajo': 4,
        'medio': 6,
        'alto': 8,
        'muy alto': 10,
    },
}

TH_FINAL = {
    'final': {
        'nulo o despreciable': 0,
        'bajo': 50,
        'medio': 75,
        'alto': 99,
        'muy alto': 140,
    }
}

ALL_THRESHOLDS = {}
ALL_THRESHOLDS.update(TH_CAT)
ALL_THRESHOLDS.update(TH_DOM)
ALL_THRESHOLDS.update(TH_FINAL)


# 11. Mapa para mostrar niveles de riesgo en mayúsculas

RISK_DISPLAY = {
    'nulo o despreciable': 'NULO',
    'bajo': 'BAJO',
    'medio': 'MEDIO',
    'alto': 'ALTO',
    'muy alto': 'MUY ALTO',
}


# 12. Nombres bonitos para categorías y dominios

DISPLAY_NAMES = {
    'ambiente_de_trabajo': 'Ambiente de trabajo',
    'factores_propios_de_la_actividad': 'Factores propios de la actividad',
    'organizacion_en_el_trabajo': 'Organización del tiempo de trabajo',
    'liderazgo_y_relaciones_en_el_trabajo': 'Liderazgo y relaciones en el trabajo',
    'entorno_organizacional': 'Entorno organizacional',
    'condiciones_deficientes_e_insalubres': 'Condiciones deficientes e insalubres',
    'trabajos_peligrosos': 'Trabajos peligrosos',
    'condiciones_en_el_ambiente_de_trabajo': 'Condiciones en el ambiente de trabajo',
    'carga_de_trabajo': 'Carga de trabajo',
    'falta_de_control_sobre_el_trabajo': 'Falta de control sobre el trabajo',
    'jornada_de_trabajo': 'Jornada de trabajo',
    'influencia_en_la_relacion_trabajo_y_familia': 'Interferencias en la relación trabajo - familia',
    'liderazgo': 'Liderazgo',
    'relaciones_en_el_trabajo': 'Relaciones en el trabajo',
    'violencia': 'Violencia',
    'reconocimiento_del_desempeno': 'Reconocimiento del desempeño',
    'insuficiente_sentido_de_pertenencia_e_inestabilidad': 'Insuficiente sentido de pertenencia e inestabilidad',
    'final': 'Calificación global',
}


# 13. Texto descriptivo de "Dimensión" para cada dominio

DOMAIN_DIM_TEXT = {
    'condiciones_en_el_ambiente_de_trabajo': [
        'Condiciones peligrosas e inseguras',
        'Condiciones deficientes e insalubres',
        'Trabajos peligrosos',
    ],
    'carga_de_trabajo': [
        'Cargas cuantitativas',
        'Ritmos de trabajo acelerado',
        'Carga mental',
        'Cargas psicológicas emocionales',
        'Cargas de alta responsabilidad',
        'Cargas contradictorias o inconsistentes',
    ],
    'falta_de_control_sobre_el_trabajo': [
        'Falta de control y autonomía sobre el trabajo',
        'Limitada o nula posibilidad de desarrollo',
        'Insuficiente participación y manejo del cambio',
        'Limitada o inexistente capacitación',
    ],
    'jornada_de_trabajo': [
        'Jornadas de trabajo extensas',
    ],
    'influencia_en_la_relacion_trabajo_y_familia': [
        'Influencia de trabajo fuera del centro laboral',
        'Influencia de las responsabilidades familiares',
    ],
    'liderazgo': [
        'Escasa claridad de funciones',
        'Características del liderazgo',
    ],
    'relaciones_en_el_trabajo': [
        'Relaciones sociales en el trabajo',
        'Deficiente relación con los colaboradores que supervisa',
    ],
    'violencia': [
        'Violencia laboral (mobbing, acoso sexual, hostigamiento sexual, violencia verbal)',
    ],
    'reconocimiento_del_desempeno': [
        'Escasa o nula retroalimentación del desempeño',
        'Escaso o nulo reconocimiento y compensación',
    ],
    'insuficiente_sentido_de_pertenencia_e_inestabilidad': [
        'Limitado sentido de pertenencia',
        'Inestabilidad laboral',
    ],
    'condiciones_deficientes_e_insalubres': [
        'Condiciones deficientes e insalubres',
    ],
    'trabajos_peligrosos': [
        'Trabajos peligrosos',
    ],
}


# 15. Listas de variables de categorías, dominios y final

CAT_VARS = [
    'ambiente_de_trabajo',
    'factores_propios_de_la_actividad',
    'organizacion_en_el_trabajo',
    'liderazgo_y_relaciones_en_el_trabajo',
    'entorno_organizacional',
]

DOM_VARS = [
    'condiciones_deficientes_e_insalubres',
    'trabajos_peligrosos',
    'condiciones_en_el_ambiente_de_trabajo',
    'carga_de_trabajo',
    'falta_de_control_sobre_el_trabajo',
    'jornada_de_trabajo',
    'influencia_en_la_relacion_trabajo_y_familia',
    'liderazgo',
    'relaciones_en_el_trabajo',
    'violencia',
    'reconocimiento_del_desempeno',
    'insuficiente_sentido_de_pertenencia_e_inestabilidad',
]


def classify_score(value, thresholds_dict):
    if pd.isna(value):
        return pd.NA

    try:
        v = float(value)
    except Exception:
        return pd.NA

    if v < 0:
        return pd.NA

    items = sorted(thresholds_dict.items(), key = lambda kv: kv[1])

    category = None
    for name, min_val in items:
        if v >= min_val:
            category = name
        else:
            break

    return category


def _normalize_str_or_na(x):
    if pd.isna(x):
        return pd.NA

    s = str(x).strip()
    if s == '' or s.lower() in ['nan', 'none', 'null', 'na', 'n/a']:
        return pd.NA

    return s


def _build_dist_table(series_in, label_col, no_spec_label = 'No especificado', order = None):
    s = series_in.copy()
    s = s.map(_normalize_str_or_na)
    s = s.fillna(no_spec_label)

    dist = (
        s
        .value_counts(dropna = False)
        .rename_axis(label_col)
        .reset_index(name = 'cantidad_colaboradores')
    )

    total = float(dist['cantidad_colaboradores'].sum()) if len(dist) > 0 else 0.0
    dist['porcentaje'] = dist['cantidad_colaboradores'] / total if total > 0 else 0.0

    if order is not None:
        order_map = {k: i for i, k in enumerate(order)}
        dist['_ord'] = dist[label_col].map(lambda x: order_map.get(x, 10_000))
        dist = dist.sort_values(['_ord', label_col]).drop(columns = ['_ord']).reset_index(drop = True)

    return dist


def build_site_report_tables(
    df_in,
    site_name = None,                # None, str, o lista de str
    sexo = None,                     # None, str, o lista de str
    rango_edad = None,               # None, str, o lista de str
    rango_antiguedad_meses = None,   # None, str, o lista de str
):
    def _as_list(x):
        if x is None:
            return None

        if isinstance(x, (list, tuple, set)):
            out = []
            for v in x:
                vv = _normalize_str_or_na(v)
                if not pd.isna(vv):
                    out.append(vv)
            return out if out else None

        x_norm = _normalize_str_or_na(x)
        if pd.isna(x_norm):
            return None

        return [x_norm]

    sites_filter = _as_list(site_name)
    sexo_filter = _as_list(sexo)
    edad_filter = _as_list(rango_edad)
    ant_filter = _as_list(rango_antiguedad_meses)

    if sites_filter is None:
        df_scope = df_in.copy()
    else:
        df_scope = df_in[df_in['site'].isin(sites_filter)].copy()

    # GENERAL solo si hay más de un site REAL en el DF filtrado
    n_sites = df_scope['site'].dropna().astype(str).nunique()
    include_general = n_sites > 1
if sexo_filter is not None:
        df_scope = df_scope[df_scope['sexo_norm'].isin(sexo_filter)].copy()

    if edad_filter is not None:
        df_scope = df_scope[df_scope['rango_edad'].isin(edad_filter)].copy()

    if ant_filter is not None:
        df_scope = df_scope[df_scope['rango_antiguedad_meses'].isin(ant_filter)].copy()

    if df_scope.empty:
        raise ValueError('No hay registros con los filtros seleccionados.')

    def _make_header_row(df_part, site_label):
        prom_final = df_part['count_final'].mean()
        med_final = df_part['count_final'].median()

        level_raw = classify_score(prom_final, TH_FINAL['final'])
        level_disp = RISK_DISPLAY.get(level_raw, level_raw)

        return {
            'site': site_label,
            'num_colaboradores': len(df_part),
            'promedio_general_organizacional': prom_final,
            'mediana_general_organizacional': med_final,
            'nivel_riesgo_organizacional': level_disp,
        }

    def _make_cat_table(df_part, site_label):
        rows = []
        for var in CAT_VARS:
            col = f'count_{var}'
            if col not in df_part.columns:
                continue

            avg = df_part[col].mean()
            med = df_part[col].median()

            level_raw = classify_score(avg, TH_CAT[var])
            level_disp = RISK_DISPLAY.get(level_raw, level_raw)

            rows.append({
                'site': site_label,
                'categoria_clave': var,
                'categoria': DISPLAY_NAMES.get(var, var.replace('_', ' ').title()),
                'calificacion_promedio': avg,
                'calificacion_mediana': med,
                'nivel_riesgo': level_disp,
            })

        return pd.DataFrame(rows)

    def _make_dom_table(df_part, site_label):
        rows = []
        for var in DOM_VARS:
            col = f'count_{var}'
            if col not in df_part.columns:
                continue

            avg = df_part[col].mean()
            med = df_part[col].median()

            thresholds = ALL_THRESHOLDS.get(var)
            if thresholds is None:
                level_disp = pd.NA
            else:
                level_raw = classify_score(avg, thresholds)
                level_disp = RISK_DISPLAY.get(level_raw, level_raw)

            rows.append({
                'site': site_label,
                'dominio_clave': var,
                'dominio': DISPLAY_NAMES.get(var, var.replace('_', ' ').title()),
                'dimension': '\n'.join(DOMAIN_DIM_TEXT.get(var, [])),
                'calificacion_promedio': avg,
                'calificacion_mediana': med,
                'nivel_riesgo': level_disp,
            })

        return pd.DataFrame(rows)

    def _make_dist_final(df_part, site_label):
        final_mapped = df_part['final'].map(
            lambda x: RISK_DISPLAY.get(str(x).lower(), str(x).upper())
        )

        dist = (
            final_mapped
            .value_counts()
            .reindex(['MUY ALTO', 'ALTO', 'MEDIO', 'BAJO', 'NULO'], fill_value = 0)
            .reset_index()
        )
        dist.columns = ['nivel_riesgo', 'cantidad_colaboradores']
        dist.insert(0, 'site', site_label)

        return dist

    def _make_demo_tables(df_part, site_label):
        df_demo_sexo = _build_dist_table(
            series_in = df_part['sexo_norm'],
            label_col = 'sexo',
            no_spec_label = 'No especificado',
            order = ['Femenino', 'Masculino', 'No binario', 'Otro', 'No especificado'],
        )
        df_demo_edad = _build_dist_table(df_part['rango_edad'], 'rango_edad')
        df_demo_ant = _build_dist_table(df_part['rango_antiguedad_meses'], 'rango_antiguedad_meses')

        df_demo_sexo.insert(0, 'site', site_label)
        df_demo_edad.insert(0, 'site', site_label)
        df_demo_ant.insert(0, 'site', site_label)

        return df_demo_sexo, df_demo_edad, df_demo_ant

    headers, cats, doms, dists = [], [], [], []
    demos_sexo, demos_edad, demos_ant = [], [], []

    sites_present = sorted(df_scope['site'].dropna().astype(str).unique().tolist())
    has_na_site = df_scope['site'].isna().any()

    for s in sites_present:
        df_part = df_scope[df_scope['site'].astype(str) == s].copy()
        if df_part.empty:
            continue

        headers.append(_make_header_row(df_part, s))
        cats.append(_make_cat_table(df_part, s))
        doms.append(_make_dom_table(df_part, s))
        dists.append(_make_dist_final(df_part, s))

        ds, de, da = _make_demo_tables(df_part, s)
        demos_sexo.append(ds)
        demos_edad.append(de)
        demos_ant.append(da)

    if has_na_site:
        df_part = df_scope[df_scope['site'].isna()].copy()
        if not df_part.empty:
            s = 'No especificado'
            headers.append(_make_header_row(df_part, s))
            cats.append(_make_cat_table(df_part, s))
            doms.append(_make_dom_table(df_part, s))
            dists.append(_make_dist_final(df_part, s))

            ds, de, da = _make_demo_tables(df_part, s)
            demos_sexo.append(ds)
            demos_edad.append(de)
            demos_ant.append(da)

    if include_general:
        g = 'GENERAL'
        headers.append(_make_header_row(df_scope, g))
        cats.append(_make_cat_table(df_scope, g))
        doms.append(_make_dom_table(df_scope, g))
        dists.append(_make_dist_final(df_scope, g))

        ds, de, da = _make_demo_tables(df_scope, g)
        demos_sexo.append(ds)
        demos_edad.append(de)
        demos_ant.append(da)

    df_header = pd.DataFrame(headers)
    df_cat = pd.concat(cats, ignore_index = True) if cats else pd.DataFrame()
    df_dom = pd.concat(doms, ignore_index = True) if doms else pd.DataFrame()
    df_cat = df_cat.drop(columns = ['categoria_clave'], errors = 'ignore')
    df_dom = df_dom.drop(columns = ['dominio_clave'], errors = 'ignore')

    df_dist = pd.concat(dists, ignore_index = True) if dists else pd.DataFrame()
    df_demo_sexo = pd.concat(demos_sexo, ignore_index = True) if demos_sexo else pd.DataFrame()
    df_demo_edad = pd.concat(demos_edad, ignore_index = True) if demos_edad else pd.DataFrame()
    df_demo_antiguedad = pd.concat(demos_ant, ignore_index = True) if demos_ant else pd.DataFrame()

    def _sort_general_last(df, site_col = 'site'):
        if df.empty or site_col not in df.columns:
            return df
        df = df.copy()
        df['_ord'] = df[site_col].map(lambda x: 1 if x == 'GENERAL' else 0)
        df = df.sort_values(['_ord', site_col]).drop(columns = ['_ord']).reset_index(drop = True)
        return df

    df_header = _sort_general_last(df_header)
    df_cat = _sort_general_last(df_cat)
    df_dom = _sort_general_last(df_dom)
    df_dist = _sort_general_last(df_dist)
    df_demo_sexo = _sort_general_last(df_demo_sexo)
    df_demo_edad = _sort_general_last(df_demo_edad)
    df_demo_antiguedad = _sort_general_last(df_demo_antiguedad)

    return (
        df_header,
        df_cat,
        df_dom,
        df_dist,
        df_demo_sexo,
        df_demo_edad,
        df_demo_antiguedad,
    )
