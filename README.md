# NOM-035 Streamlit

App para consolidar archivos NOM-035 (layout clasificado), preparar demográficos y generar reportes por **site** y **GENERAL**.

## Layout esperado (clasificado)
Los archivos subidos deben incluir, como mínimo:
- `site`
- `count_final`
- `final`
- columnas `count_*` (por ejemplo `count_ambiente_de_trabajo`, etc.)

## Ejecutar local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud
1. Sube este repo a GitHub.
2. Conecta el repo desde Streamlit Cloud.
3. Entry point: `app.py`
