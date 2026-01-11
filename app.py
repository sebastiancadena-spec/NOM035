import streamlit as st
import pandas as pd

from src.auth import require_login
from src.io_utils import load_many_files, get_site_name_from_filename
from src.nom35_core import ensure_classified_layout
from src.nom35_prepare import prepare_nom35_dataframe
from src.nom35_report import build_site_report_tables

from src.diagnostics import get_env_diagnostics

# Diagnóstico de entorno (útil en Streamlit Cloud)
with st.expander('Diagnóstico del entorno', expanded = False):
    st.json(get_env_diagnostics())

# Si falta openpyxl, no permitimos continuar con .xlsx (evita crash)
try:
    import openpyxl  # noqa: F401
except Exception:
    st.error(
        'No está disponible la librería "openpyxl" en este entorno, por eso no se pueden leer archivos .xlsx. '
        'Solución: en Streamlit Cloud ve a Manage app → Reboot (y si sigue igual, Clear cache) para que reinstale '
        'requirements.txt. Alternativa temporal: sube los archivos en CSV.'
    )



VALID_TOKEN = 'drag0n.2026!'

st.set_page_config(page_title = 'NOM-035 | Reportes', layout = 'wide')
require_login(valid_token = VALID_TOKEN)

st.title('NOM-035 | Consolidador y Reportes')

st.markdown(
    """
**Instructivo**
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

# Editor de sites por archivo
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

st.subheader('Parámetros demográficos')
c1, c2 = st.columns(2)
with c1:
    edad_step = st.number_input('Corte de edad (step)', min_value = 1, max_value = 20, value = 5, step = 1)
with c2:
    antiguedad_step = st.number_input('Corte de antigüedad (meses, step)', min_value = 1, max_value = 60, value = 5, step = 1)

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

with st.spinner('Procesando archivos...'):
    df_raw = load_many_files(uploaded_files, site_overrides = site_overrides)

df_raw = df_raw = ensure_classified_layout(df_raw)

nom35_final = prepare_nom35_dataframe(df_raw, edad_step = int(edad_step), antiguedad_step = int(antiguedad_step))

st.success('Listo. Se generó el dataset consolidado.')

st.subheader('Filtros del reporte')

sites_all = sorted(nom35_final['site'].dropna().astype(str).unique().tolist())
sexo_all = sorted(nom35_final['sexo_norm'].dropna().astype(str).unique().tolist())

edad_num = pd.to_numeric(nom35_final['edad_num'], errors = 'coerce')
edad_min = int(edad_num.min(skipna = True)) if not pd.isna(edad_num.min(skipna = True)) else 18
edad_max = int(edad_num.max(skipna = True)) if not pd.isna(edad_num.max(skipna = True)) else 60

ant_num = pd.to_numeric(nom35_final['antiguedad_total_meses'], errors = 'coerce')
ant_min = int(ant_num.min(skipna = True)) if not pd.isna(ant_num.min(skipna = True)) else 0
ant_max = int(ant_num.max(skipna = True)) if not pd.isna(ant_num.max(skipna = True)) else 120

f1, f2, f3 = st.columns([2, 2, 3])
with f1:
    site_filter = st.multiselect('Site', options = sites_all, default = sites_all)
with f2:
    sexo_filter = st.multiselect('Sexo', options = sexo_all, default = sexo_all)
with f3:
    edad_range = st.slider('Edad (min-max)', min_value = edad_min, max_value = edad_max, value = (edad_min, edad_max))

ant_range = st.slider('Antigüedad (meses, min-max)', min_value = ant_min, max_value = ant_max, value = (ant_min, ant_max))

df_view = nom35_final.copy()

if site_filter:
    df_view = df_view[df_view['site'].isin(site_filter)].copy()

if sexo_filter:
    df_view = df_view[df_view['sexo_norm'].isin(sexo_filter)].copy()

df_view = df_view[
    (pd.to_numeric(df_view['edad_num'], errors = 'coerce').fillna(-1) >= edad_range[0]) &
    (pd.to_numeric(df_view['edad_num'], errors = 'coerce').fillna(-1) <= edad_range[1])
].copy()

df_view = df_view[
    (pd.to_numeric(df_view['antiguedad_total_meses'], errors = 'coerce').fillna(-1) >= ant_range[0]) &
    (pd.to_numeric(df_view['antiguedad_total_meses'], errors = 'coerce').fillna(-1) <= ant_range[1])
].copy()

if df_view.empty:
    st.warning('No hay registros con estos filtros.')
    st.stop()

(df_header, df_cat, df_dom, df_dist, df_demo_sexo, df_demo_edad, df_demo_antiguedad) = build_site_report_tables(
    df_view,
    site_name = None
)

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