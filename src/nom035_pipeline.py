
# 6. Librerías base
import os, re, unicodedata
from typing import List
import pandas as pd
import numpy as np

# 7. Utilidades de normalización
def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))

def normalize_col(c: str) -> str:
    c2 = _strip_accents(str(c)).strip().lower()
    c2 = re.sub(r"[^\w\s]+", "", c2)
    c2 = re.sub(r"\s+", "_", c2)
    return c2

def normalize_str(x):
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    if s == "":
        return np.nan
    s2 = _strip_accents(s).lower()
    s2 = re.sub(r"\s+", " ", s2)
    return s2

# 8. Lectura robusta

def read_any_excel(path: str) -> pd.DataFrame:
    """
    Robust Excel reader:
    - Tries default engine first.
    - If fails and file is .xlsx/.xlsm -> tries openpyxl (optional dependency).
    - If fails and file is .xls -> tries xlrd (optional dependency).
    - Normalizes headers and strings.
    """
    try:
        df = pd.read_excel(path, dtype="object")  # let pandas choose engine
    except Exception:
        lower = str(path).lower()
        engine = None
        if lower.endswith((".xlsx", ".xlsm")):
            engine = "openpyxl"
        elif lower.endswith(".xls"):
            engine = "xlrd"
        if engine is None:
            raise
        df = pd.read_excel(path, dtype="object", engine=engine)

    if (sum(str(c).startswith("Unnamed") for c in df.columns) / max(len(df.columns), 1)) >= 0.6:
        try:
            df = pd.read_excel(path, dtype="object", header=1)
        except Exception:
            pass
    df.columns = [normalize_col(c) for c in df.columns]
    df = df.dropna(axis=1, how="all")
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].map(normalize_str)
    return df

# 9. Heurísticas columna
NAME_CANDS = ["nombre", "nombre_completo", "name", "empleado", "colaborador", "nombres_y_apellidos"]
EMAIL_CANDS = ["correo", "email", "e_mail", "mail", "correo_electronico"]

def pick_first_present(df, cands):
    for c in cands:
        if c in df.columns:
            return c
    for c in df.columns:
        for pat in cands:
            if pat in c:
                return c
    return None

# 10. Región desde nombre de archivo
def infer_region_from_filename(path: str) -> str:
    base = _strip_accents(os.path.basename(path)).lower()
    if "izucar" in base: return "izucar"
    if "lerma" in base and "empeco" in base: return "empeco l"
    if "empeco" in base: return "empeco c"
    if "cuautla" in base: return "cuautla"
    if "san" in base and "jeron" in base: return "san jeronimo"
    if "lerma" in base: return "lerma"
    return "desconocido"

# 11. ID y filtro
def build_id(df):
    name_col = pick_first_present(df, NAME_CANDS)
    email_col = pick_first_present(df, EMAIL_CANDS)
    df["_name"] = (df[name_col] if name_col else pd.Series([np.nan]*len(df))).astype(str).replace({"nan": np.nan})
    df["_email"] = (df[email_col] if email_col else pd.Series([np.nan]*len(df))).astype(str).replace({"nan": np.nan})
    df["id_key"] = df["_email"].fillna(df["_name"])
    # eliminar anónimos
    mask_keep = ~(df["_name"].isna() & df["_email"].isna())
    if name_col:
        mask_keep &= ~df["_name"].str.contains("anon", na=False)
    return df.loc[mask_keep].copy()

# 12. Consolidación principal
def consolidate(captura_paths: List[str], cuestionario_paths: List[str]) -> pd.DataFrame:
    frames = []
    for path in captura_paths + cuestionario_paths:
        df = read_any_excel(path)
        df["source_file"] = os.path.basename(path)
        df["region"] = infer_region_from_filename(path)
        frames.append(build_id(df))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# 13. EDA helpers
def categorical_share_by_region(df: pd.DataFrame, col: str, region_col: str = "region") -> pd.DataFrame:
    tab = pd.crosstab(df[region_col], df[col], normalize="index") * 100
    return tab.reset_index().rename_axis(None, axis=1)

def chisq_by_region(df: pd.DataFrame, col: str, region_col: str = "region") -> float:
    from scipy.stats import chi2_contingency
    tab = pd.crosstab(df[region_col], df[col])
    if tab.shape[0] < 2 or tab.shape[1] < 2:
        return np.nan
    _, p, _, _ = chi2_contingency(tab)
    return p
