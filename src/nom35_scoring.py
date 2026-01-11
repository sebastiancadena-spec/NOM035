from __future__ import annotations

import pandas as pd
import numpy as np
import re
import unicodedata

from src.nom35_report import ALL_THRESHOLDS, RISK_DISPLAY, classify_score

def to_snake_case(col_name: str) -> str:
    """
    Limpia un nombre de columna y lo convierte a snake_case:
    - Normaliza acentos (á -> a, etc.)
    - Elimina caracteres especiales (deja solo letras y espacios)
    - Pasa a minúsculas
    - Reemplaza espacios por guiones bajos
    """
    # Aseguramos que sea string
    text = str(col_name)

    # 2.1 Normalizar a NFKD para separar letras de acentos
    text = unicodedata.normalize('NFKD', text)

    # 2.2 Eliminar acentos (caracteres de combinación)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))

    # 2.3 Dejar solo letras y espacios (todo lo demás se vuelve espacio)
    text = re.sub(r'[^A-Za-z\s]', ' ', text)

    # 2.4 Pasar a minúsculas
    text = text.lower()

    # 2.5 Reemplazar grupos de espacios por un solo guion bajo
    text = re.sub(r'\s+', '_', text)

    # 2.6 Quitar guiones bajos al inicio o al final
    text = text.strip('_')

    return text


def get_site_name(path: Path) -> str:
    """
    A partir del nombre de archivo genera el 'site'.
    Ejemplo:
    - 'SAN_JERONIMO-94.xlsx' -> 'SAN JERONIMO'
    """
    # Quitamos la extensión: 'SAN_JERONIMO-94'
    stem = path.stem

    # Nos quedamos con la parte antes del guion: 'SAN_JERONIMO'
    letters_part = stem.split('-')[0]

    # Reemplazamos guiones bajos por espacios: 'SAN JERONIMO'
    site = letters_part.replace('_', ' ')

    return site


def load_single_file(path: Path) -> pd.DataFrame:
    """
    Lee un archivo individual (xlsx/xls/csv),
    limpia nombres de columnas a snake_case y
    agrega columnas 'archivo_origen' y 'site'.
    """
    # 72.7 Leer el archivo según la extensión
    suffix = path.suffix.lower()

    if suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(path)
    elif suffix == '.csv':
        df = pd.read_csv(path)
    else:
        raise ValueError(f'Extensión no soportada: {suffix} en archivo {path.name}')

    # 2.8 Copiar por seguridad
    df = df.copy()

    # 2.9 Limpiar y convertir nombres de columnas a snake_case
    df.columns = [to_snake_case(c) for c in df.columns]

    # 2.10 Agregar columna con nombre completo del archivo
    df['archivo_origen'] = path.name

    # 2.11 Agregar columna con nombre de site (solo letras)
    df['site'] = get_site_name(path)

    return df


# 3. Función principal de construcción del DataFrame maestro
def build_nom35_dataset(inputs_dir: Path) -> pd.DataFrame:
    """
    Recorre la carpeta de inputs, lee todos los archivos soportados,
    estandariza columnas y concatena en un solo DataFrame.
    """
    # 3.1 Listar archivos soportados en la carpeta
    all_files = [
        p for p in inputs_dir.iterdir()
        if p.is_file() and p.suffix.lower() in ('.xlsx', '.xls', '.csv')
    ]

    if not all_files:
        raise FileNotFoundError(f'No se encontraron archivos xlsx/xls/csv en {inputs_dir}')

    # 3.2 Cargar cada archivo individualmente aplicando la misma lógica
    frames = []
    for path in all_files:
        print(f'Leyendo archivo: {path.name}')
        df = load_single_file(path)
        frames.append(df)

    # 3.3 Concatenar todos los DataFrames en uno solo
    full_df = pd.concat(frames, ignore_index=True)

    return full_df


# 4. Ejecución del pipeline
if __name__ == '__main__':
    # 4.1 Construir el DataFrame maestro
    nom35_df = build_nom35_dataset(inputs_dir)

    # 4.2 Ordenar y eliminar duplicados for fecha de témino (formulario) y correo
    nom35_df.sort_values(by = ['correo_electronico', 'hora_de_finalizacion'], ascending = [True, False], inplace = True)
    nom35_df.drop_duplicates(subset = 'correo_electronico', inplace = True)
    nom35_df.reset_index(drop = True, inplace = True)

    # 4.3 Mostrar un resumen rápido
    print('\nResumen del DataFrame maestro')
    print('Filas totales :', len(nom35_df))
    print('Columnas      :', len(nom35_df.columns))
    print('\nPrimeras columnas:')
    print(nom35_df.columns.tolist()[:20])

    # # 4.4 (Opcional) Guardar el resultado en una carpeta outputs
    # outputs_dir = base_dir / 'outputs'
    # outputs_dir.mkdir(exist_ok = True)

    # output_path = outputs_dir / 'nom35_respuestas_consolidadas.xlsx'
    # nom35_df.to_excel(output_path, index = False)

    # print(f'\nArchivo consolidado guardado en: {output_path}')

# 5. Pipeline para agregar calificaciones numéricas

import numpy as np


# 5.1 Listas de preguntas por tipo de escala

ASC_COLS = [
    'el_espacio_donde_trabajo_me_permite_realizar_mis_actividades_de_manera_segura_e_higienica',
    'considero_que_en_mi_trabajo_se_aplican_las_normas_de_seguridad_y_salud_en_el_trabajo',
    'mi_trabajo_permite_que_desarrolle_nuevas_habilidades',
    'en_mi_trabajo_puedo_aspirar_a_un_mejor_puesto',
    'durante_mi_jornada_de_trabajo_puedo_tomar_pausas_cuando_las_necesito',
    'puedo_decidir_cuanto_trabajo_realizo_durante_la_jornada_laboral',
    'puedo_decidir_la_velocidad_a_la_que_realizo_mis_actividades_en_mi_trabajo',
    'puedo_cambiar_el_orden_de_las_actividades_que_realizo_en_mi_trabajo',
    'cuando_se_presentan_cambios_en_mi_trabajo_se_tienen_en_cuenta_mis_ideas_o_aportaciones',
    'me_informan_con_claridad_cuales_son_mis_funciones',
    'me_explican_claramente_los_resultados_que_debo_obtener_en_mi_trabajo',
    'me_explican_claramente_los_objetivos_de_mi_trabajo',
    'me_informan_con_quien_puedo_resolver_problemas_o_asuntos_de_trabajo',
    'me_permiten_asistir_a_capacitaciones_relacionadas_con_mi_trabajo',
    'recibo_capacitacion_util_para_hacer_mi_trabajo',
    'mi_jefe_ayuda_a_organizar_mejor_el_trabajo',
    'mi_jefe_tiene_en_cuenta_mis_puntos_de_vista_y_opiniones',
    'mi_jefe_me_comunica_a_tiempo_la_informacion_relacionada_con_el_trabajo',
    'la_orientacion_que_me_da_mi_jefe_me_ayuda_a_realizar_mejor_mi_trabajo',
    'mi_jefe_ayuda_a_solucionar_los_problemas_que_se_presentan_en_el_trabajo',
    'puedo_confiar_en_mis_companeros_de_trabajo',
    'entre_companeros_solucionamos_los_problemas_de_trabajo_de_forma_respetuosa',
    'en_mi_trabajo_me_hacen_sentir_parte_del_grupo',
    'cuando_tenemos_que_realizar_trabajo_de_equipo_los_companeros_colaboran',
    'mis_companeros_de_trabajo_me_ayudan_cuando_tengo_dificultades',
    'me_informan_sobre_lo_que_hago_bien_en_mi_trabajo',
    'la_forma_como_evaluan_mi_trabajo_en_mi_centro_de_trabajo_me_ayuda_a_mejorar_mi_desempeno',
    'en_mi_centro_de_trabajo_me_pagan_a_tiempo_mi_salario',
    'el_pago_que_recibo_es_el_que_merezco_por_el_trabajo_que_realizo',
    'si_obtengo_los_resultados_esperados_en_mi_trabajo_me_recompensan_o_reconocen',
    'las_personas_que_hacen_bien_el_trabajo_pueden_crecer_laboralmente',
    'considero_que_mi_trabajo_es_estable',
    'siento_orgullo_de_laborar_en_este_centro_de_trabajo',
    'me_siento_comprometido_con_mi_trabajo',
    'en_mi_trabajo_puedo_expresarme_libremente_sin_interrupciones',
]

DESC_COLS = [
    'mi_trabajo_me_exige_hacer_mucho_esfuerzo_fisico',
    'me_preocupa_sufrir_un_accidente_en_mi_trabajo',
    'considero_que_las_actividades_que_realizo_son_peligrosas',
    'por_la_cantidad_de_trabajo_que_tengo_debo_quedarme_tiempo_adicional_a_mi_turno',
    'por_la_cantidad_de_trabajo_que_tengo_debo_trabajar_sin_parar',
    'considero_que_es_necesario_mantener_un_ritmo_de_trabajo_acelerado',
    'mi_trabajo_exige_que_este_muy_concentrado',
    'mi_trabajo_requiere_que_memorice_mucha_informacion',
    'en_mi_trabajo_tengo_que_tomar_decisiones_dificiles_muy_rapido',
    'mi_trabajo_exige_que_atienda_varios_asuntos_al_mismo_tiempo',
    'en_mi_trabajo_soy_responsable_de_cosas_de_mucho_valor',
    'respondo_ante_mi_jefe_por_los_resultados_de_toda_mi_area_de_trabajo',
    'en_el_trabajo_me_dan_ordenes_contradictorias',
    'considero_que_en_mi_trabajo_me_piden_hacer_cosas_innecesarias',
    'trabajo_horas_extras_mas_de_tres_veces_a_la_semana',
    'mi_trabajo_me_exige_laborar_en_dias_de_descanso_festivos_o_fines_de_semana',
    'considero_que_el_tiempo_en_el_trabajo_es_mucho_y_perjudica_mis_actividades_familiares_o_personales',
    'debo_atender_asuntos_de_trabajo_cuando_estoy_en_casa',
    'pienso_en_las_actividades_familiares_o_personales_cuando_estoy_en_mi_trabajo',
    'pienso_que_mis_responsabilidades_familiares_afectan_mi_trabajo',
    'los_cambios_que_se_presentan_en_mi_trabajo_dificultan_mi_labor',
    'en_mi_trabajo_existe_continua_rotacion_de_personal',
    'recibo_criticas_constantes_a_mi_persona_y_o_trabajo',
    'recibo_burlas_calumnias_difamaciones_humillaciones_o_ridiculizaciones',
    'se_ignora_mi_presencia_o_se_me_excluye_de_las_reuniones_de_trabajo_y_en_la_toma_de_decisiones',
    'se_manipulan_las_situaciones_de_trabajo_para_hacerme_parecer_un_mal_trabajador',
    'se_ignoran_mis_exitos_laborales_y_se_atribuyen_a_otros_trabajadores',
    'me_bloquean_o_impiden_las_oportunidades_que_tengo_para_obtener_ascenso_o_mejora_en_mi_trabajo',
    'he_presenciado_actos_de_violencia_en_mi_centro_de_trabajo',
    'atiendo_clientes_o_usuarios_muy_enojados',
    'mi_trabajo_me_exige_atender_personas_muy_necesitadas_de_ayuda_o_enfermas',
    'para_hacer_mi_trabajo_debo_demostrar_sentimientos_distintos_a_los_mios',
    'mi_trabajo_me_exige_atender_situaciones_de_violencia',
    'comunican_tarde_los_asuntos_de_trabajo',
    'dificultan_el_logro_de_los_resultados_del_trabajo',
    'cooperan_poco_cuando_se_necesita',
    'ignoran_las_sugerencias_para_mejorar_su_trabajo',
]

BOOL_COLS = [
    'en_mi_trabajo_debo_brindar_servicio_a_clientes_o_usuarios_areas_o_personas_con_quienes_colaboramos_directamente_ya_sea_porque_reciben_un_entregable_un_servicio_o_forman_parte_de_algun_proceso_e',
    'soy_jefe_de_otros_trabajadores',
]


# 5.2 Normalizador de texto para respuestas

def normalize_text(x):
    if pd.isna(x):
        return None

    text = str(x).strip().lower()

    # quitar acentos
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))

    # colapsar espacios internos
    text = re.sub(r'\s+', ' ', text)

    return text


# 5.3 Mapeos base para la escala Likert

LIKERT_ASC = {
    'nunca': 0,
    'casi nunca': 1,
    'algunas veces': 2,
    'casi siempre': 3,
    'siempre': 4,
}

LIKERT_DESC = {
    'nunca': 4,
    'casi nunca': 3,
    'algunas veces': 2,
    'casi siempre': 1,
    'siempre': 0,
}

def likert_to_score(x, orientation = 'asc'):
    """
    Convierte una respuesta tipo 'Nunca', 'Casi nunca', etc.
    a su puntaje correspondiente según la orientación.
    """
    norm = normalize_text(x)
    if norm is None:
        return np.nan

    if orientation == 'asc':
        return LIKERT_ASC.get(norm, np.nan)
    else:
        return LIKERT_DESC.get(norm, np.nan)

BOOL_MAP = {
    'si': 1,
    'no': 0,
}

def bool_to_score(x):
    norm = normalize_text(x)
    if norm is None:
        return np.nan
    # por si quedó 'si' o 'sí'
    norm = norm.replace('í', 'i')
    return BOOL_MAP.get(norm, np.nan)


# 5.5 Función principal para agregar columnas de score

def add_scores(df: pd.DataFrame) -> pd.DataFrame:
    df_scored = df.copy()

    # Ascendentes
    for col in ASC_COLS:
        if col in df_scored.columns:
            new_col = f'score__{col}'
            df_scored[new_col] = df_scored[col].apply(likert_to_score, orientation = 'asc')

    # Descendentes
    for col in DESC_COLS:
        if col in df_scored.columns:
            new_col = f'score__{col}'
            df_scored[new_col] = df_scored[col].apply(likert_to_score, orientation = 'desc')

    # Booleanos
    for col in BOOL_COLS:
        if col in df_scored.columns:
            new_col = f'score__{col}'
            df_scored[new_col] = df_scored[col].apply(bool_to_score)

    return df_scored

GROUPS = {
    'count_ambiente_de_trabajo': [
        'el_espacio_donde_trabajo_me_permite_realizar_mis_actividades_de_manera_segura_e_higienica',
        'me_preocupa_sufrir_un_accidente_en_mi_trabajo',
    ],
    'count_factores_propios_de_la_actividad': [
        'por_la_cantidad_de_trabajo_que_tengo_debo_quedarme_tiempo_adicional_a_mi_turno',
        'por_la_cantidad_de_trabajo_que_tengo_debo_trabajar_sin_parar',
        'considero_que_es_necesario_mantener_un_ritmo_de_trabajo_acelerado',
        'mi_trabajo_exige_que_este_muy_concentrado',
        'mi_trabajo_requiere_que_memorice_mucha_informacion',
        'en_mi_trabajo_tengo_que_tomar_decisiones_dificiles_muy_rapido',
        'mi_trabajo_exige_que_atienda_varios_asuntos_al_mismo_tiempo',
        'en_mi_trabajo_soy_responsable_de_cosas_de_mucho_valor',
        'respondo_ante_mi_jefe_por_los_resultados_de_toda_mi_area_de_trabajo',
        'en_el_trabajo_me_dan_ordenes_contradictorias',
        'considero_que_en_mi_trabajo_me_piden_hacer_cosas_innecesarias',
        'mi_trabajo_permite_que_desarrolle_nuevas_habilidades',
        'en_mi_trabajo_puedo_aspirar_a_un_mejor_puesto',
        'durante_mi_jornada_de_trabajo_puedo_tomar_pausas_cuando_las_necesito',
        'puedo_decidir_cuanto_trabajo_realizo_durante_la_jornada_laboral',
        'puedo_decidir_la_velocidad_a_la_que_realizo_mis_actividades_en_mi_trabajo',
        'puedo_cambiar_el_orden_de_las_actividades_que_realizo_en_mi_trabajo',
        'los_cambios_que_se_presentan_en_mi_trabajo_dificultan_mi_labor',
        'cuando_se_presentan_cambios_en_mi_trabajo_se_tienen_en_cuenta_mis_ideas_o_aportaciones',
        'me_permiten_asistir_a_capacitaciones_relacionadas_con_mi_trabajo',
        'recibo_capacitacion_util_para_hacer_mi_trabajo',
        'atiendo_clientes_o_usuarios_muy_enojados',
        'mi_trabajo_me_exige_atender_personas_muy_necesitadas_de_ayuda_o_enfermas',
        'para_hacer_mi_trabajo_debo_demostrar_sentimientos_distintos_a_los_mios',
        'mi_trabajo_me_exige_atender_situaciones_de_violencia',
    ],
    'count_organizacion_en_el_trabajo': [
        'trabajo_horas_extras_mas_de_tres_veces_a_la_semana',
        'mi_trabajo_me_exige_laborar_en_dias_de_descanso_festivos_o_fines_de_semana',
        'considero_que_el_tiempo_en_el_trabajo_es_mucho_y_perjudica_mis_actividades_familiares_o_personales',
        'debo_atender_asuntos_de_trabajo_cuando_estoy_en_casa',
        'pienso_en_las_actividades_familiares_o_personales_cuando_estoy_en_mi_trabajo',
        'pienso_que_mis_responsabilidades_familiares_afectan_mi_trabajo',
    ],
    'count_liderazgo_y_relaciones_en_el_trabajo': [
        'me_informan_con_claridad_cuales_son_mis_funciones',
        'me_explican_claramente_los_resultados_que_debo_obtener_en_mi_trabajo',
        'me_explican_claramente_los_objetivos_de_mi_trabajo',
        'me_informan_con_quien_puedo_resolver_problemas_o_asuntos_de_trabajo',
        'mi_jefe_ayuda_a_organizar_mejor_el_trabajo',
        'mi_jefe_tiene_en_cuenta_mis_puntos_de_vista_y_opiniones',
        'mi_jefe_me_comunica_a_tiempo_la_informacion_relacionada_con_el_trabajo',
        'la_orientacion_que_me_da_mi_jefe_me_ayuda_a_realizar_mejor_mi_trabajo',
        'mi_jefe_ayuda_a_solucionar_los_problemas_que_se_presentan_en_el_trabajo',
        'puedo_confiar_en_mis_companeros_de_trabajo',
        'entre_companeros_solucionamos_los_problemas_de_trabajo_de_forma_respetuosa',
        'en_mi_trabajo_me_hacen_sentir_parte_del_grupo',
        'cuando_tenemos_que_realizar_trabajo_de_equipo_los_companeros_colaboran',
        'mis_companeros_de_trabajo_me_ayudan_cuando_tengo_dificultades',
        'en_mi_trabajo_puedo_expresarme_libremente_sin_interrupciones',
        'recibo_criticas_constantes_a_mi_persona_y_o_trabajo',
        'recibo_burlas_calumnias_difamaciones_humillaciones_o_ridiculizaciones',
        'se_ignora_mi_presencia_o_se_me_excluye_de_las_reuniones_de_trabajo_y_en_la_toma_de_decisiones',
        'se_manipulan_las_situaciones_de_trabajo_para_hacerme_parecer_un_mal_trabajador',
        'se_ignoran_mis_exitos_laborales_y_se_atribuyen_a_otros_trabajadores',
        'me_bloquean_o_impiden_las_oportunidades_que_tengo_para_obtener_ascenso_o_mejora_en_mi_trabajo',
        'he_presenciado_actos_de_violencia_en_mi_centro_de_trabajo',
        'comunican_tarde_los_asuntos_de_trabajo',
        'dificultan_el_logro_de_los_resultados_del_trabajo',
        'cooperan_poco_cuando_se_necesita',
        'ignoran_las_sugerencias_para_mejorar_su_trabajo',
    ],
    'count_entorno_organizacional': [
        'me_informan_sobre_lo_que_hago_bien_en_mi_trabajo',
        'la_forma_como_evaluan_mi_trabajo_en_mi_centro_de_trabajo_me_ayuda_a_mejorar_mi_desempeno',
        'en_mi_centro_de_trabajo_me_pagan_a_tiempo_mi_salario',
        'el_pago_que_recibo_es_el_que_merezco_por_el_trabajo_que_realizo',
        'si_obtengo_los_resultados_esperados_en_mi_trabajo_me_recompensan_o_reconocen',
        'las_personas_que_hacen_bien_el_trabajo_pueden_crecer_laboralmente',
        'considero_que_mi_trabajo_es_estable',
        'en_mi_trabajo_existe_continua_rotacion_de_personal',
        'siento_orgullo_de_laborar_en_este_centro_de_trabajo',
        'me_siento_comprometido_con_mi_trabajo',
    ],
    'count_condiciones_deficientes_e_insalubres': [
        'mi_trabajo_me_exige_hacer_mucho_esfuerzo_fisico',
        'considero_que_en_mi_trabajo_se_aplican_las_normas_de_seguridad_y_salud_en_el_trabajo',
    ],
    'count_trabajos_peligrosos': [
        'considero_que_las_actividades_que_realizo_son_peligrosas',
    ],
    'count_condiciones_en_el_ambiente_de_trabajo': [
        'el_espacio_donde_trabajo_me_permite_realizar_mis_actividades_de_manera_segura_e_higienica',
        'me_preocupa_sufrir_un_accidente_en_mi_trabajo',
    ],
    'count_carga_de_trabajo': [
        'por_la_cantidad_de_trabajo_que_tengo_debo_quedarme_tiempo_adicional_a_mi_turno',
        'por_la_cantidad_de_trabajo_que_tengo_debo_trabajar_sin_parar',
        'considero_que_es_necesario_mantener_un_ritmo_de_trabajo_acelerado',
        'mi_trabajo_exige_que_este_muy_concentrado',
        'mi_trabajo_requiere_que_memorice_mucha_informacion',
        'en_mi_trabajo_tengo_que_tomar_decisiones_dificiles_muy_rapido',
        'mi_trabajo_exige_que_atienda_varios_asuntos_al_mismo_tiempo',
        'en_mi_trabajo_soy_responsable_de_cosas_de_mucho_valor',
        'respondo_ante_mi_jefe_por_los_resultados_de_toda_mi_area_de_trabajo',
        'en_el_trabajo_me_dan_ordenes_contradictorias',
        'considero_que_en_mi_trabajo_me_piden_hacer_cosas_innecesarias',
        'atiendo_clientes_o_usuarios_muy_enojados',
        'mi_trabajo_me_exige_atender_personas_muy_necesitadas_de_ayuda_o_enfermas',
        'para_hacer_mi_trabajo_debo_demostrar_sentimientos_distintos_a_los_mios',
        'mi_trabajo_me_exige_atender_situaciones_de_violencia',
    ],
    'count_falta_de_control_sobre_el_trabajo': [
        'mi_trabajo_permite_que_desarrolle_nuevas_habilidades',
        'en_mi_trabajo_puedo_aspirar_a_un_mejor_puesto',
        'durante_mi_jornada_de_trabajo_puedo_tomar_pausas_cuando_las_necesito',
        'puedo_decidir_cuanto_trabajo_realizo_durante_la_jornada_laboral',
        'puedo_decidir_la_velocidad_a_la_que_realizo_mis_actividades_en_mi_trabajo',
        'puedo_cambiar_el_orden_de_las_actividades_que_realizo_en_mi_trabajo',
        'los_cambios_que_se_presentan_en_mi_trabajo_dificultan_mi_labor',
        'cuando_se_presentan_cambios_en_mi_trabajo_se_tienen_en_cuenta_mis_ideas_o_aportaciones',
        'me_permiten_asistir_a_capacitaciones_relacionadas_con_mi_trabajo',
        'recibo_capacitacion_util_para_hacer_mi_trabajo',
    ],
    'count_jornada_de_trabajo': [
        'trabajo_horas_extras_mas_de_tres_veces_a_la_semana',
        'mi_trabajo_me_exige_laborar_en_dias_de_descanso_festivos_o_fines_de_semana',
    ],
    'count_influencia_en_la_relacion_trabajo_y_familia': [
        'considero_que_el_tiempo_en_el_trabajo_es_mucho_y_perjudica_mis_actividades_familiares_o_personales',
        'debo_atender_asuntos_de_trabajo_cuando_estoy_en_casa',
        'pienso_en_las_actividades_familiares_o_personales_cuando_estoy_en_mi_trabajo',
        'pienso_que_mis_responsabilidades_familiares_afectan_mi_trabajo',
    ],
    'count_liderazgo': [
        'me_informan_con_claridad_cuales_son_mis_funciones',
        'me_explican_claramente_los_resultados_que_debo_obtener_en_mi_trabajo',
        'me_explican_claramente_los_objetivos_de_mi_trabajo',
        'me_informan_con_quien_puedo_resolver_problemas_o_asuntos_de_trabajo',
        'mi_jefe_ayuda_a_organizar_mejor_el_trabajo',
        'mi_jefe_tiene_en_cuenta_mis_puntos_de_vista_y_opiniones',
        'mi_jefe_me_comunica_a_tiempo_la_informacion_relacionada_con_el_trabajo',
        'la_orientacion_que_me_da_mi_jefe_me_ayuda_a_realizar_mejor_mi_trabajo',
        'mi_jefe_ayuda_a_solucionar_los_problemas_que_se_presentan_en_el_trabajo',
    ],
    'count_relaciones_en_el_trabajo': [
        'puedo_confiar_en_mis_companeros_de_trabajo',
        'entre_companeros_solucionamos_los_problemas_de_trabajo_de_forma_respetuosa',
        'en_mi_trabajo_me_hacen_sentir_parte_del_grupo',
        'cuando_tenemos_que_realizar_trabajo_de_equipo_los_companeros_colaboran',
        'mis_companeros_de_trabajo_me_ayudan_cuando_tengo_dificultades',
        'comunican_tarde_los_asuntos_de_trabajo',
        'dificultan_el_logro_de_los_resultados_del_trabajo',
        'cooperan_poco_cuando_se_necesita',
        'ignoran_las_sugerencias_para_mejorar_su_trabajo',
    ],
    'count_violencia': [
        'en_mi_trabajo_puedo_expresarme_libremente_sin_interrupciones',
        'recibo_criticas_constantes_a_mi_persona_y_o_trabajo',
        'recibo_burlas_calumnias_difamaciones_humillaciones_o_ridiculizaciones',
        'se_ignora_mi_presencia_o_se_me_excluye_de_las_reuniones_de_trabajo_y_en_la_toma_de_decisiones',
        'se_manipulan_las_situaciones_de_trabajo_para_hacerme_parecer_un_mal_trabajador',
        'se_ignoran_mis_exitos_laborales_y_se_atribuyen_a_otros_trabajadores',
        'me_bloquean_o_impiden_las_oportunidades_que_tengo_para_obtener_ascenso_o_mejora_en_mi_trabajo',
        'he_presenciado_actos_de_violencia_en_mi_centro_de_trabajo',
    ],
    'count_reconocimiento_del_desempeno': [
        'me_informan_sobre_lo_que_hago_bien_en_mi_trabajo',
        'la_forma_como_evaluan_mi_trabajo_en_mi_centro_de_trabajo_me_ayuda_a_mejorar_mi_desempeno',
        'en_mi_centro_de_trabajo_me_pagan_a_tiempo_mi_salario',
        'el_pago_que_recibo_es_el_que_merezco_por_el_trabajo_que_realizo',
        'si_obtengo_los_resultados_esperados_en_mi_trabajo_me_recompensan_o_reconocen',
        'las_personas_que_hacen_bien_el_trabajo_pueden_crecer_laboralmente',
    ],
    'count_insuficiente_sentido_de_pertenencia_e_inestabilidad': [
        'considero_que_mi_trabajo_es_estable',
        'en_mi_trabajo_existe_continua_rotacion_de_personal',
        'siento_orgullo_de_laborar_en_este_centro_de_trabajo',
        'me_siento_comprometido_con_mi_trabajo',
    ],
}


# 7. Función para agregar columnas de conteo por grupo

def add_group_counts(df, groups_dict):
    """
    A partir de un DataFrame con columnas score__...
    agrega las columnas count_* sumando los scores de cada grupo.
    También agrega 'count_final' como suma de todos los score__.
    """
    df_out = df.copy()

    # 7.1 Para cada grupo, buscamos las columnas score__ correspondientes
    for group_name, base_cols in groups_dict.items():
        score_cols = []
        missing = []

        for col in base_cols:
            score_col = f'score__{col}'
            if score_col in df_out.columns:
                score_cols.append(score_col)
            else:
                missing.append(col)

        if missing:
            print(f'ATENCIÓN: en {group_name} faltan columnas score__: {missing}')

        if score_cols:
            df_out[group_name] = df_out[score_cols].sum(axis = 1, min_count = 1)
        else:
            df_out[group_name] = pd.NA

    # 7.2 count_final = suma de todas las columnas score__*
    all_score_cols = [c for c in df_out.columns if c.startswith('score__')]
    df_out['count_final'] = df_out[all_score_cols].sum(axis = 1, min_count = 1)

    return df_out

TARGET_VARS = [
    'ambiente_de_trabajo',
    'factores_propios_de_la_actividad',
    'organizacion_en_el_trabajo',
    'liderazgo_y_relaciones_en_el_trabajo',
    'entorno_organizacional',
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
    'final',
]


def classify_nom35_dataframe(df_in: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline end-to-end para formularios RAW:
    1) snake_case de columnas
    2) scores por reactivo (score__*)
    3) counts por grupo (count_*)
    4) clasificación por umbrales -> columnas (ambiente_de_trabajo, ..., final)
    """
    df = df_in.copy()

    # 1) normalizar headers a snake_case
    df.columns = [to_snake_case(c) for c in df.columns]

    # 2) scores + 3) counts
    df_scored = add_scores(df)
    df_counts = add_group_counts(df_scored, GROUPS)

    # 4) clasificación (categorías, dominios y final)
    df_classified = df_counts.copy()

    for var in TARGET_VARS:
        if var == 'final':
            source_col = 'count_final'
        else:
            source_col = f'count_{var}'

        if source_col not in df_classified.columns:
            continue

        thresholds = ALL_THRESHOLDS.get(var)
        if thresholds is None:
            continue

        df_classified[var] = df_classified[source_col].apply(lambda x: classify_score(x, thresholds))
        df_classified[var] = df_classified[var].map(lambda x: RISK_DISPLAY.get(x, x))

    return df_classified


def ensure_or_classify(df_in: pd.DataFrame) -> pd.DataFrame:
    """
    Si el DF ya viene clasificado (tiene count_final/final y count_*), lo deja.
    Si no, intenta clasificarlo desde RAW.
    """
    has_min = ('count_final' in df_in.columns) and ('final' in df_in.columns)
    has_any_counts = any([c.startswith('count_') for c in df_in.columns])

    if has_min and has_any_counts:
        return df_in.copy()

    return classify_nom35_dataframe(df_in)
