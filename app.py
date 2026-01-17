import streamlit as st
import pandas as pd

from src.auth import require_login
from src.io_utils import load_many_files, get_site_name_from_filename
from src.nom35_core import ensure_classified_layout
from src.nom35_prepare import prepare_nom35_dataframe
from src.nom35_report import build_site_report_tables, DISPLAY_NAMES, DOMAIN_DIM_TEXT
from src.nom35_scoring import GROUPS
from src.diagnostics import get_env_diagnostics


VALID_TOKEN = 'Dragon.2026!'


def _range_sort_key(v):
    """
    Orden lógico para rangos tipo:
      - '<18'
      - '0-2', '18-20', '21-30', ...
      - 'No especificado'
    """
    if pd.isna(v):
        return (2, 10_000_000, '')

    s = str(v).strip()

    if s.lower() == 'no especificado':
        return (2, 10_000_000, s)

    if s == '<18':
        return (0, -1, s)

    try:
        left = s.split('-')[0].strip()
        return (1, int(left), s)
    except Exception:
        return (1, 9_999_999, s)


def _clear_all_filters():
    st.session_state['flt_site'] = []
    st.session_state['flt_sexo'] = []
    st.session_state['flt_area'] = []
    st.session_state['flt_jefe'] = []
    st.session_state['flt_correo'] = []
    st.session_state['flt_edad_rango'] = []
    st.session_state['flt_ant_rango'] = []
    st.rerun()


def _pretty_question_name(q_col: str) -> str:
    """
    Convierte el nombre de la columna (snake_case largo) a algo legible.
    """
    if not isinstance(q_col, str):
        return str(q_col)

    s = q_col.replace('_', ' ').strip()
    if s == '':
        return q_col

    return s[:1].upper() + s[1:]


def _build_group_detail_table(df_in: pd.DataFrame, site_col: str, question_cols: list[str]) -> pd.DataFrame:
    """
    Construye una tabla tipo:
      site | reactivo | promedio | mediana | n_validos

    Usa score__{reactivo} si existe; si no, intenta usar el reactivo tal cual (numérico).
    """
    df = df_in.copy()

    sites = sorted(df[site_col].dropna().astype(str).unique().tolist()) if site_col in df.columns else []
    include_general = len(sites) > 1

    rows = []

    for q in question_cols:
        score_col = f'score__{q}'
        base_col = score_col if score_col in df.columns else q

        if base_col not in df.columns:
            continue

        # Nos aseguramos de que sea numérico para promedio/mediana
        s_all = pd.to_numeric(df[base_col], errors = 'coerce')

        # Por site
        for site in sites:
            s_site = pd.to_numeric(df.loc[df[site_col].astype(str) == site, base_col], errors = 'coerce')
            n_valid = int(s_site.notna().sum())

            rows.append({
                'site': site,
                'reactivo': _pretty_question_name(q),
                'promedio': float(s_site.mean(skipna = True)) if n_valid > 0 else pd.NA,
                'mediana': float(s_site.median(skipna = True)) if n_valid > 0 else pd.NA,
                'n_validos': n_valid,
            })

        # GENERAL (si aplica)
        if include_general:
            n_valid = int(s_all.notna().sum())
            rows.append({
                'site': 'GENERAL',
                'reactivo': _pretty_question_name(q),
                'promedio': float(s_all.mean(skipna = True)) if n_valid > 0 else pd.NA,
                'mediana': float(s_all.median(skipna = True)) if n_valid > 0 else pd.NA,
                'n_validos': n_valid,
            })

    out = pd.DataFrame(rows)

    if out.empty:
        return out

    # Orden: site (GENERAL al final), luego reactivo alfabético
    out['_ord'] = out['site'].map(lambda x: 1 if x == 'GENERAL' else 0)
    out = out.sort_values(['_ord', 'site', 'reactivo']).drop(columns = ['_ord']).reset_index(drop = True)

    return out


def _get_category_keys():
    """
    Categorías = las primeras 5 (count_*) según TARGET_VARS (mismo orden que en reportes)
    """
    return [
        'ambiente_de_trabajo',
        'factores_propios_de_la_actividad',
        'organizacion_en_el_trabajo',
        'liderazgo_y_relaciones_en_el_trabajo',
        'entorno_organizacional',
    ]


def _get_domain_keys():
    """
    Dominios = los 12 dominios + 2 dominios "guía" (condiciones_deficientes..., trabajos_peligrosos)
    (mismo set que manejas en reportes)
    """
    return [
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


st.set_page_config(page_title = 'NOM-035 | Reportes', layout = 'wide')
require_login(valid_token = VALID_TOKEN)

st.title('NOM-035 | Consolidador y Reportes')

with st.expander('Diagnóstico del entorno', expanded = False):
    st.json(get_env_diagnostics())

try:
    import openpyxl  # noqa: F401
except Exception:
    st.error(
        'No está disponible la librería "openpyxl" en este entorno, por eso no se pueden leer archivos .xlsx. '
        'Solución: en Streamlit Cloud ve a Manage app → Reboot (y si sigue igual, Clear cache) para que reinstale '
        'requirements.txt. Alternativa temporal: sube los archivos en CSV.'
    )

st.markdown(
    """
**Instructivo general**
- Sube archivos **.xlsx** o **.csv** con layout NOM-035 (clasificado).
- Para que la app detecte la planta automáticamente: el archivo debe iniciar con `PLANTA_EN_MAYUSCULAS-...`
  - Ejemplo: `EMPECO_C-69.xlsx` → `EMPECO C`
- Plantas registradas: **EMPECO C, EMPECO L, IZUCAR, LERMA, SAN JERONIMO**
"""
)

uploaded_files = st.file_uploader(
    'Sube tus archivos',
    type = ['xlsx', 'csv'],
    accept_multiple_files = True
)

if not uploaded_files:
    st.stop()

st.subheader('Archivos detectados')
st.write(f'Archivos cargados: {len(uploaded_files)}')

default_sites = {}
for i, f in enumerate(uploaded_files, start = 1):
    guess = get_site_name_from_filename(f.name)

    if '-' not in f.name:
        if guess == '' or guess == 'PLANTA01':
            guess = f'PLANTA{str(i).zfill(2)}'

    default_sites[f.name] = guess

st.caption('Confirma/edita el nombre final de planta por archivo (esto alimenta la columna site).')

site_overrides = {}
for f in uploaded_files:
    col1, col2 = st.columns([2, 3])
    with col1:
        st.write(f'**{f.name}**')
    with col2:
        site_overrides[f.name] = st.text_input(
            label = 'site',
            value = default_sites[f.name],
            key = f'site_{f.name}',
        )

st.divider()

# ------------------------------------------------------------
# Parámetros demográficos
# ------------------------------------------------------------
st.subheader('Parámetros demográficos')

with st.expander('Cómo funcionan estos cortes (lee esto antes de procesar)', expanded = False):
    st.markdown(
        """
**Edad**
- La app siempre separa primero el rango **18-20**.
- Si existen edades menores a 18, se etiquetan como **`<18`**.
- Después, el resto se agrupa con el tamaño que selecciones:
  - **Rangos de 5 años:** 21-25, 26-30, 31-35, ...
  - **Rangos de 10 años:** 21-30, 31-40, 41-50, ...

**Antigüedad (en meses)**
- La antigüedad se calcula como: `antiguedad_ano * 12 + antiguedad_meses`.
- El valor **0** siempre queda dentro del primer corte (esto es intencional).
"""
    )

edad_options = {
    'Rangos de 5 años (recomendado)': 5,
    'Rangos de 10 años': 10,
}

antiguedad_options = {
    'Bimestre (2 meses)': 2,
    'Trimestre (3 meses)': 3,
    'Cuatrimestre (4 meses)': 4,
    'Semestre (6 meses)': 6,
    'Año (12 meses)': 12,
}

c1, c2 = st.columns(2)
with c1:
    edad_label = st.selectbox(
        'Corte de edad',
        options = list(edad_options.keys()),
        index = 0
    )
with c2:
    antiguedad_label = st.selectbox(
        'Corte de antigüedad (en meses)',
        options = list(antiguedad_options.keys()),
        index = 0
    )

edad_step = int(edad_options[edad_label])
antiguedad_step = int(antiguedad_options[antiguedad_label])

if 'results_ready' not in st.session_state:
    st.session_state['results_ready'] = False

col_a, col_b = st.columns([1, 1])
with col_a:
    run_process = st.button('Procesar / Reprocesar')
with col_b:
    if st.button('Limpiar resultados'):
        st.session_state['results_ready'] = False
        st.session_state.pop('nom35_final', None)
        st.rerun()

if run_process:
    st.session_state['results_ready'] = True

if not st.session_state.get('results_ready', False):
    st.stop()

# ------------------------------------------------------------
# Procesamiento
# ------------------------------------------------------------
with st.spinner('Procesando archivos...'):
    df_raw = load_many_files(uploaded_files, site_overrides = site_overrides)

df_raw = ensure_classified_layout(df_raw)

nom35_final = prepare_nom35_dataframe(
    df_raw,
    edad_step = edad_step,
    antiguedad_step = antiguedad_step
)

st.success('Listo. Se generó el dataset consolidado.')

# ------------------------------------------------------------
# Filtros del reporte
# ------------------------------------------------------------
st.subheader('Filtros del reporte')
st.caption('Si no seleccionas nada en un filtro, se interpreta como "ver todo".')

st.button('Limpiar todos los filtros', on_click = _clear_all_filters)

sites_all = sorted(nom35_final['site'].dropna().astype(str).unique().tolist())
sexo_all = sorted(nom35_final['sexo_norm'].dropna().astype(str).unique().tolist())

area_all = sorted(nom35_final['area'].dropna().astype(str).unique().tolist()) if 'area' in nom35_final.columns else []
correo_all = sorted(nom35_final['correo_electronico'].dropna().astype(str).unique().tolist()) if 'correo_electronico' in nom35_final.columns else []
jefe_all = sorted(nom35_final['nombre_de_jefe_inmediato'].dropna().astype(str).unique().tolist()) if 'nombre_de_jefe_inmediato' in nom35_final.columns else []

edad_rangos_all = []
if 'rango_edad' in nom35_final.columns:
    edad_rangos_all = nom35_final['rango_edad'].dropna().astype(str).unique().tolist()
    edad_rangos_all = sorted(edad_rangos_all, key = _range_sort_key)

ant_rangos_all = []
if 'rango_antiguedad_meses' in nom35_final.columns:
    ant_rangos_all = nom35_final['rango_antiguedad_meses'].dropna().astype(str).unique().tolist()
    ant_rangos_all = sorted(ant_rangos_all, key = _range_sort_key)

f1, f2, f3 = st.columns([2, 2, 2])
with f1:
    site_filter = st.multiselect('Site', options = sites_all, default = [], key = 'flt_site')
with f2:
    sexo_filter = st.multiselect('Sexo', options = sexo_all, default = [], key = 'flt_sexo')
with f3:
    area_filter = st.multiselect('Área', options = area_all, default = [], key = 'flt_area')

g1, g2, g3 = st.columns([2, 2, 2])
with g1:
    jefe_filter = st.multiselect('Jefe inmediato', options = jefe_all, default = [], key = 'flt_jefe')
with g2:
    correo_filter = st.multiselect('Correo electrónico', options = correo_all, default = [], key = 'flt_correo')
with g3:
    edad_rango_filter = st.multiselect('Rango de edad', options = edad_rangos_all, default = [], key = 'flt_edad_rango')

ant_rango_filter = st.multiselect(
    'Rango de antigüedad (meses)',
    options = ant_rangos_all,
    default = [],
    key = 'flt_ant_rango'
)

# Aplicación de filtros (solo si el usuario selecciona algo)
df_view = nom35_final.copy()

if len(site_filter) > 0:
    df_view = df_view[df_view['site'].isin(site_filter)].copy()

if len(sexo_filter) > 0 and 'sexo_norm' in df_view.columns:
    df_view = df_view[df_view['sexo_norm'].isin(sexo_filter)].copy()

if len(area_filter) > 0 and 'area' in df_view.columns:
    df_view = df_view[df_view['area'].astype(str).isin(area_filter)].copy()

if len(jefe_filter) > 0 and 'nombre_de_jefe_inmediato' in df_view.columns:
    df_view = df_view[df_view['nombre_de_jefe_inmediato'].astype(str).isin(jefe_filter)].copy()

if len(correo_filter) > 0 and 'correo_electronico' in df_view.columns:
    df_view = df_view[df_view['correo_electronico'].astype(str).isin(correo_filter)].copy()

if len(edad_rango_filter) > 0 and 'rango_edad' in df_view.columns:
    df_view = df_view[df_view['rango_edad'].astype(str).isin(edad_rango_filter)].copy()

if len(ant_rango_filter) > 0 and 'rango_antiguedad_meses' in df_view.columns:
    df_view = df_view[df_view['rango_antiguedad_meses'].astype(str).isin(ant_rango_filter)].copy()

if df_view.empty:
    st.warning('No hay registros con estos filtros.')
    st.stop()

# ------------------------------------------------------------
# Sección 1: Resultados originales (tabs existentes)
# ------------------------------------------------------------
(
    df_header,
    df_cat,
    df_dom,
    df_dist,
    df_demo_sexo,
    df_demo_edad,
    df_demo_antiguedad
) = build_site_report_tables(df_view, site_name = None)

st.subheader('Resultados')

tabs = st.tabs([
    'Header',
    'Categorías',
    'Dominios',
    'Distribución Final',
    'Demo Sexo',
    'Demo Edad',
    'Demo Antigüedad',
])

with tabs[0]:
    st.dataframe(df_header, use_container_width = True)
with tabs[1]:
    st.dataframe(df_cat, use_container_width = True)
with tabs[2]:
    st.dataframe(df_dom, use_container_width = True)
with tabs[3]:
    st.dataframe(df_dist, use_container_width = True)
with tabs[4]:
    st.dataframe(df_demo_sexo, use_container_width = True)
with tabs[5]:
    st.dataframe(df_demo_edad, use_container_width = True)
with tabs[6]:
    st.dataframe(df_demo_antiguedad, use_container_width = True)

# ------------------------------------------------------------
# Sección 2: Zoom por CATEGORÍAS (tabs nuevas abajo)
# ------------------------------------------------------------
st.divider()
st.subheader('Detalle por categoría (zoom)')

category_keys = _get_category_keys()
category_tab_names = [DISPLAY_NAMES.get(k, k.replace('_', ' ').title()) for k in category_keys]
cat_tabs = st.tabs(category_tab_names)

for tab, cat_key in zip(cat_tabs, category_keys):
    with tab:
        group_name = f'count_{cat_key}'
        question_cols = GROUPS.get(group_name, [])

        st.caption(
            'Promedios y medianas por site para cada reactivo que compone esta categoría '
            '(usando columnas score__* cuando existan).'
        )

        df_detail = _build_group_detail_table(
            df_in = df_view,
            site_col = 'site',
            question_cols = question_cols
        )

        if df_detail.empty:
            st.warning('No se encontraron reactivos para esta categoría en el dataset actual.')
        else:
            st.dataframe(df_detail, use_container_width = True)

# ------------------------------------------------------------
# Sección 3: Zoom por DOMINIOS (tabs nuevas abajo)
# ------------------------------------------------------------
st.divider()
st.subheader('Detalle por dominio (zoom)')

domain_keys = _get_domain_keys()
domain_tab_names = [DISPLAY_NAMES.get(k, k.replace('_', ' ').title()) for k in domain_keys]
dom_tabs = st.tabs(domain_tab_names)

for tab, dom_key in zip(dom_tabs, domain_keys):
    with tab:
        group_name = f'count_{dom_key}'
        question_cols = GROUPS.get(group_name, [])

        dim_lines = DOMAIN_DIM_TEXT.get(dom_key, [])
        if dim_lines:
            st.caption('Dimensiones asociadas: ' + ' | '.join(dim_lines))

        st.caption(
            'Promedios y medianas por site para cada reactivo que compone este dominio '
            '(usando columnas score__* cuando existan).'
        )

        df_detail = _build_group_detail_table(
            df_in = df_view,
            site_col = 'site',
            question_cols = question_cols
        )

        if df_detail.empty:
            st.warning('No se encontraron reactivos para este dominio en el dataset actual.')
        else:
            st.dataframe(df_detail, use_container_width = True)
