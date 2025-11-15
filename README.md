
# NOM-035 — Consolidador y Reporte

![status](https://img.shields.io/badge/status-dev-blue) ![python](https://img.shields.io/badge/Python-3.11+-yellow) ![license](https://img.shields.io/badge/license-MIT-green)

## Objetivo
Unificar respuestas de **Captura** y **Cuestionario** NOM-035, depurar anónimos, construir un **ID** (correo→nombre),
y entregar una base maestra + reporte/EDA por **región** (Izúcar, Lerma, Empeco C, Empeco L, etc.).

## Estructura
```
src/
  nom035_pipeline.py
streamlit_app.py
README.md
consolidado_nom035.csv         # generado como ejemplo
reporte_mckinsey_nom035.md     # plantilla de reporte
```

## Uso local
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip wheel
pip install pandas numpy scipy streamlit plotly openpyxl
streamlit run streamlit_app.py
```

## Metodología (resumen)
- **Normalización de columnas** y textos (minúsculas, sin acentos, sin caracteres especiales).
- **ID jerárquico:** correo (si existe) → nombre normalizado.
- **Eliminación de anónimos** (sin nombre y sin correo, o nombre que contenga 'anon').
- **Región** inferida desde el nombre del archivo.
- **EDA** por región (tablas porcentuales y **chi-cuadrado** para p-values).

## Roadmap
- Mapear dimensiones NOM-035 a columnas reales para gráficos comparables por región.
- Kruskal–Wallis para ordinales (Likert 0–4).
- Multivariado (MCA/FAMD) + clustering.
- Exportación de reporte PDF con narrativa ejecutiva.
