
import streamlit as st
import pandas as pd
import numpy as np
from src.nom035_pipeline import consolidate, read_any_excel, categorical_share_by_region, chisq_by_region

st.set_page_config(page_title="NOM-035 — Consolidador", layout="wide")
st.title("NOM-035 — Consolidador y Reporte (versión GitHub)")

st.markdown(
    "Sube tus archivos **Captura** y **Cuestionario** (varios), y el archivo **HC** si lo deseas. "
    "El sistema limpiará encabezados, unificará columnas, eliminará anónimos y generará tablas por región."
)

captura_files = st.file_uploader("Captura (varios)", type=["xlsx","xls"], accept_multiple_files=True)
cuestionario_files = st.file_uploader("Cuestionario (varios)", type=["xlsx","xls"], accept_multiple_files=True)
hc_file = st.file_uploader("HC (opcional)", type=["xlsx","xls"])

if st.button("Procesar") and (captura_files or cuestionario_files):
    with st.spinner("Procesando..."):
        def save_tmp(fs):
            paths = []
            for f in fs:
                p = f"/tmp/{f.name}"
                with open(p, "wb") as out:
                    out.write(f.getbuffer())
                paths.append(p)
            return paths

        cap_paths = save_tmp(captura_files) if captura_files else []
        cue_paths = save_tmp(cuestionario_files) if cuestionario_files else []

        df = consolidate(cap_paths, cue_paths)
        st.success(f"Observaciones consolidadas: {len(df):,}")
        st.dataframe(df.head(50))

        # EDA simple
        if "region" in df.columns:
            st.subheader("Conteo por región")
            st.dataframe(df["region"].value_counts(dropna=False).rename_axis("region").reset_index(name="n"))

        # Descarga CSV
        st.download_button("Descargar base consolidada (CSV)",
                           df.to_csv(index=False).encode("utf-8"),
                           file_name="consolidado_nom035.csv")
