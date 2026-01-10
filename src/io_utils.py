from __future__ import annotations

import re
from pathlib import Path
import pandas as pd


def get_site_name_from_filename(filename: str) -> str:
    """
    Regla:
    - Toma lo que va antes de '-' (si existe)
    - Reemplaza '_' por ' '
    - Si no hay '-', usa el stem (antes del punto)
    - Si queda vacío, devuelve 'PLANTA01' (la app lo renombra si hace falta)
    """
    name = Path(filename).name
    stem = Path(name).stem

    if '-' in stem:
        left = stem.split('-')[0].strip()
    else:
        left = stem.strip()

    left = left.replace('_', ' ')
    left = re.sub(r'\s+', ' ', left).strip()

    if left == '':
        return 'PLANTA01'

    return left


def load_single_file(uploaded_file, site_override: str | None = None) -> pd.DataFrame:
    """
    Carga XLSX o CSV desde Streamlit UploadedFile.
    Agrega:
    - archivo_origen
    - site (override si viene, si no: inferido del nombre)
    """
    filename = uploaded_file.name

    try:
        if filename.lower().endswith('.xlsx'):
            # No forzamos engine; pandas selecciona openpyxl para xlsx cuando está instalado
            df = pd.read_excel(uploaded_file)
        elif filename.lower().endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            raise ValueError(f'Formato no soportado: {filename}. Sube .xlsx o .csv')
    except ImportError as e:
        raise ImportError(
            'No se pudo leer el archivo .xlsx porque falta la dependencia "openpyxl" '
            'en el entorno. En Streamlit Cloud se arregla asegurando que exista en '
            'requirements.txt y reiniciando la app (Manage app → Reboot / Clear cache). Recomendado: fijar Python 3.11 con runtime.txt.'
        ) from e

    df = df.copy()
    df['archivo_origen'] = filename

    site_guess = get_site_name_from_filename(filename)
    df['site'] = site_override if site_override is not None else site_guess

    return df


def load_many_files(uploaded_files, site_overrides: dict[str, str]) -> pd.DataFrame:
    """
    Concatena todos los archivos en un solo DF.
    site_overrides: { filename: site_final }
    """
    dfs = []
    for f in uploaded_files:
        site_final = site_overrides.get(f.name)
        dfs.append(load_single_file(f, site_override = site_final))

    out = pd.concat(dfs, ignore_index = True)
    return out
