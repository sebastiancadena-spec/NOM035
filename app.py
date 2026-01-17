import streamlit as st
import pandas as pd

from src.auth import require_login
from src.io_utils import load_many_files, get_site_name_from_filename
from src.nom35_core import ensure_classified_layout
from src.nom35_prepare import prepare_nom35_dataframe
from src.nom35_report import build_site_report_tables
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
# 6) Parámetros demográficos (listas)
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
- El valor **0 siempre queda dentro del primer corte** (esto es intencional).
- Ejemplos:
  - **Bimestre (2 meses):** 0-2, 3-4, 5-6, ...
  - **Trimestre (3 meses):** 0-3, 4-6, 7-9, 10-12, ...
  - **Cuatrimestre (4 meses):** 0-4, 5-8, 9-12, ...
  - **Semestre (6 meses):** 0-6, 7-12, 13-18, ...
  - **Año (12 meses):** 0-12, 13-24, 25-36, ...
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
# 7) Filtros del reporte
#    Reglas UX:
#      - Por default: NO seleccionar nada y VER TODO
#      - En cuanto seleccione algo: FILTRAR
# ------------------------------------------------------------
st.subheader('Filtros del reporte')
st.caption('Tip: si no seleccionas nada en un filtro, se interpreta como "ver todo".')

sites_all = sorted(nom35_final['site'].dropna().astype(str).unique().tolist())
sexo_all = sorted(nom35_final['sexo_norm'].dropna().astype(str).unique().tolist())

# Nuevos filtros solicitados
area_all = sorted(nom35_final['area'].dropna().astype(str).unique().tolist()) if 'area' in nom35_final.columns else []
correo_all = sorted(nom35_final['correo_electronico'].dropna().astype(str).unique().tolist()) if 'correo_electronico' in nom35_final.columns else []
jefe_all = sorted(nom35_final['nombre_de_jefe_inmediato'].dropna().astype(str).unique().tolist()) if 'nombre_de_jefe_inmediato' in nom35_final.columns else []

# Edad y antigüedad como LISTAS basadas en los rangos ya calculados (dependen del step elegido)
edad_rangos_all = []
if 'rango_edad' in nom35_final.columns:
    edad_rangos_all = nom35_final['rango_edad'].dropna().astype(str).unique().tolist()
    edad_rangos_all = sorted(edad_rangos_all, key = _range_sort_key)

ant_rangos_all = []
if 'rango_antiguedad_meses' in nom35_final.columns:
    ant_rangos_all = nom35_final['rango_antiguedad_meses'].dropna().astype(str).unique().tolist()
    ant_rangos_all = sorted(ant_rangos_all, key = _range_sort_key)

# Controles
f1, f2, f3 = st.columns([2, 2, 2])
with f1:
    site_filter = st.multiselect('Site', options = sites_all, default = [])
with f2:
    sexo_filter = st.multiselect('Sexo', options = sexo_all, default = [])
with f3:
    area_filter = st.multiselect('Área', options = area_all, default = [])

g1, g2, g3 = st.columns([2, 2, 2])
with g1:
    jefe_filter = st.multiselect('Jefe inmediato', options = jefe_all, default = [])
with g2:
    correo_filter = st.multiselect('Correo electrónico', options = correo_all, default = [])
with g3:
    edad_rango_filter = st.multiselect('Rango de edad', options = edad_rangos_all, default = [])

ant_rango_filter = st.multiselect(
    'Rango de antigüedad (meses)',
    options = ant_rangos_all,
    default = []
)

# Aplicación de filtros:
# - Si la lista está vacía: NO filtra (equivale a "ver todo")
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
# 8) Tablas
# ------------------------------------------------------------
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
