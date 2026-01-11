from __future__ import annotations

import re
import unicodedata
import pandas as pd
import numpy as np

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


# 5.4 Mapeo para booleanos (Sí/No)
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
    norm = normalize_text(x)
    if norm is None:
        return np.nan

    if orientation == 'asc':
        return LIKERT_ASC.get(norm, np.nan)
    else:
        return LIKERT_DESC.get(norm, np.nan)

# 5.4 Mapeo para booleanos (Sí/No)
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


# 5.6 Aplicar el pipeline de scoring a nom35_df
nom35_scored_df = add_scores(nom35_df)

print('Columnas totales (incluyendo scores):', len(nom35_scored_df.columns))

# Ejemplo: ver algunas columnas de score
[s for s in nom35_scored_df.columns if s.startswith('score__')][:10]

# 6. Definición de grupos de preguntas (sin el prefijo score__)

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


# 8. Aplicar a tu DataFrame nom35_scored_df

nom35_with_counts_df = add_group_counts(nom35_scored_df, GROUPS)

print('Columnas totales (incluyendo counts):', len(nom35_with_counts_df.columns))
[col for col in nom35_with_counts_df.columns if col.startswith('count_')]

# 9.1 Umbrales por CATEGORÍA (primer tabla)
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

# 9.2 Umbrales por DOMINIO (segunda tabla)
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

# 9.3 Umbrales para la calificación FINAL (tercer tabla)
TH_FINAL = {
    'final': {
        'nulo o despreciable': 0,
        'bajo': 50,
        'medio': 75,
        'alto': 99,
        'muy alto': 140,
    }
}

# 9.4 Función para clasificar dado un valor numérico y un diccionario de umbrales

def classify_score(value, thresholds_dict):
    """
    Asigna la categoría de riesgo según los umbrales mínimos.
    Ejemplo: { 'nulo o despreciable': 0, 'bajo': 15, 'medio': 21, ... }
    Se toma la categoría con el MAYOR umbral que sea <= valor.
    """
    if pd.isna(value):
        return pd.NA

    try:
        v = float(value)
    except Exception:
        return pd.NA

    if v < 0:
        return pd.NA

    # Ordenar por valor de umbral ascendente
    items = sorted(thresholds_dict.items(), key = lambda kv: kv[1])

    category = None
    for name, min_val in items:
        if v >= min_val:
            category = name
        else:
            break

    return category

# 9.5 Combinar todos los umbrales en un solo dict
ALL_THRESHOLDS = {}
ALL_THRESHOLDS.update(TH_CAT)
ALL_THRESHOLDS.update(TH_DOM)
ALL_THRESHOLDS.update(TH_FINAL)

# 9.6 Lista de columnas objetivo (las que quieres SIN 'count_')
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

# 9.7 Crear una copia para trabajar
nom35_classified_df = nom35_with_counts_df.copy()

# 9.8 Crear columnas categóricas a partir de los count_
for var in TARGET_VARS:
    if var == 'final':
        source_col = 'count_final'
    else:
        source_col = f'count_{var}'

    if source_col not in nom35_classified_df.columns:
        print(f'ATENCIÓN: columna {source_col} no encontrada, se omite {var}')
        continue

    if var not in ALL_THRESHOLDS:
        print(f'ATENCIÓN: no hay umbrales definidos para {var}')
        continue

    thresholds = ALL_THRESHOLDS[var]

    new_col = var  # nombre sin 'count_'
    nom35_classified_df[new_col] = nom35_classified_df[source_col].apply(
        lambda x: classify_score(x, thresholds)
    )

# 9.9 Checar resultado rápido
cols_check = [c for c in nom35_classified_df.columns if c.startswith('count_')] + TARGET_VARS
cols_check

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


# 14. Función para clasificar un valor según los umbrales

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


# 16. Helpers para normalización / bins / dist

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
    if total > 0:
        dist['porcentaje'] = dist['cantidad_colaboradores'] / total
    else:
        dist['porcentaje'] = 0.0

    if order is not None:
        order_map = {k: i for i, k in enumerate(order)}
        dist['_ord'] = dist[label_col].map(lambda x: order_map.get(x, 10_000))
        dist = dist.sort_values(['_ord', label_col]).drop(columns = ['_ord']).reset_index(drop = True)

    return dist


def _bin_numeric_series(
    series_in,
    step,
    start_value,
    no_spec_label = 'No especificado',
    min_value_allowed = None,
):
    s = pd.to_numeric(series_in, errors = 'coerce')

    if min_value_allowed is not None:
        s = s.where(s >= min_value_allowed, other = pd.NA)

    bins = []
    labels = []

    s_max = s.max(skipna = True)
    if pd.isna(s_max):
        out = pd.Series([no_spec_label] * len(series_in), index = series_in.index)
        return out

    max_val = int(s_max)

    low = int(start_value)
    high = int(start_value + step - 1)

    while low <= max_val:
        bins.append((low, high))
        labels.append(f'{low}-{high}')
        low = high + 1
        high = low + step - 1

    def _assign_bin(v):
        if pd.isna(v):
            return no_spec_label

        try:
            vv = int(float(v))
        except Exception:
            return no_spec_label

        for (b_low, b_high), lab in zip(bins, labels):
            if b_low <= vv <= b_high:
                return lab

        if vv < bins[0][0]:
            return labels[0]

        return labels[-1]

    return s.map(_assign_bin)


def _build_age_bins(series_age, step = 5, no_spec_label = 'No especificado'):
    age_num = pd.to_numeric(series_age, errors = 'coerce')
    age_num = age_num.where(age_num >= 0, other = pd.NA)

    if step == 5:
        s_max = age_num.max(skipna = True)
        if pd.isna(s_max):
            return pd.Series([no_spec_label] * len(series_age), index = series_age.index)

        max_val = int(s_max)

        bins = [(18, 20)]
        labels = ['18-20']

        low = 21
        high = 25
        while low <= max_val:
            bins.append((low, high))
            labels.append(f'{low}-{high}')
            low = high + 1
            high = low + 4

        def _assign(v):
            if pd.isna(v):
                return no_spec_label

            try:
                vv = int(float(v))
            except Exception:
                return no_spec_label

            if vv < 18:
                return no_spec_label

            for (b_low, b_high), lab in zip(bins, labels):
                if b_low <= vv <= b_high:
                    return lab

            return labels[-1]

        return age_num.map(_assign)

    binned_tail = _bin_numeric_series(
        series_in = age_num,
        step = int(step),
        start_value = 21,
        no_spec_label = no_spec_label,
        min_value_allowed = 0,
    )

    def _merge(v):
        if pd.isna(v):
            return no_spec_label

        try:
            vv = int(float(v))
        except Exception:
            return no_spec_label

        if vv < 18:
            return no_spec_label

        if 18 <= vv <= 20:
            return '18-20'

        return binned_tail.loc[v.name]

    return age_num.map(_merge)


def _build_tenure_months_bins(ant_ano, ant_meses, step = 5, no_spec_label = 'No especificado'):
    a = pd.to_numeric(ant_ano, errors = 'coerce')
    m = pd.to_numeric(ant_meses, errors = 'coerce')

    total = a * 12 + m
    total = total.where(total >= 0, other = pd.NA)

    return _bin_numeric_series(
        series_in = total,
        step = int(step),
        start_value = 0,
        no_spec_label = no_spec_label,
        min_value_allowed = 0,
    )


def _normalize_sexo(series_in):
    sexo_series = series_in.map(_normalize_str_or_na)

    def _norm(v):
        if pd.isna(v):
            return pd.NA

        s = str(v).strip().lower()

        if s in ['m', 'masc', 'masculino', 'hombre', 'varon', 'varón']:
            return 'Hombre'
        if s in ['f', 'fem', 'femenino', 'mujer']:
            return 'Mujer'

        return str(v).strip()

    return sexo_series.map(_norm)


def _strip_accents(text):
    import unicodedata

    if pd.isna(text):
        return pd.NA

    s = str(text)
    s = ''.join([c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)])
    return s


def _only_letters_and_spaces(text):
    if pd.isna(text):
        return pd.NA

    s = str(text)
    s = re.sub(r'[^A-Za-z\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _proper_name(text):
    if pd.isna(text):
        return pd.NA

    s = str(text).strip()
    if s == '':
        return pd.NA

    # title() funciona bastante bien para "Nombre Propio" general
    return s.lower().title()


def _homologate_text_value(value):
    s = _normalize_str_or_na(value)
    if pd.isna(s):
        return pd.NA

    s = _strip_accents(s)
    s = _only_letters_and_spaces(s)
    s = _proper_name(s)

    return s


# 17. NUEVA función: preparar dataframe (agregar columnas demográficas + homologar texto)

def prepare_nom35_dataframe(df_in, edad_step = 5, antiguedad_step = 5):
    df = df_in.copy()

    # Requiere: re (para regex) y pandas (pd) ya importados en tu notebook/script.
    # Si no lo tienes: import re

    # 17.1 Homologación de columnas de texto (sin acentos/sin signos/solo letras/Nombre Propio)
    cols_to_homologate = [
        'primer_nombre',
        'segundo_nombre',
        'primer_apellido',
        'segundo_apellido',
        'nombre_de_jefe_inmediato',
        'coloca_tu_puesto_actual',
        'area',
        'selecciona_el_tipo_de_posicion_que_tienes',
    ]

    for c in cols_to_homologate:
        if c in df.columns:
            df[c] = df[c].map(_homologate_text_value)

    # 17.2 Normalizar sexo y crear sexo_norm (útil para filtros)
    if 'sexo' in df.columns:
        df['sexo_norm'] = _normalize_sexo(df['sexo']).fillna('No especificado')
    else:
        df['sexo_norm'] = 'No especificado'

    # 17.3 Crear rango de edad (bins) para filtros y reportes
    if 'edad' in df.columns:
        df['rango_edad'] = _build_age_bins(
            series_age = df['edad'],
            step = int(edad_step),
            no_spec_label = 'No especificado',
        ).fillna('No especificado')
    else:
        df['rango_edad'] = 'No especificado'

    # 17.4 Crear antigüedad total en meses + rango de antigüedad (bins)
    if 'antiguedad_ano' in df.columns and 'antiguedad_meses' in df.columns:
        a = pd.to_numeric(df['antiguedad_ano'], errors = 'coerce')
        m = pd.to_numeric(df['antiguedad_meses'], errors = 'coerce')

        total_meses = a * 12 + m
        total_meses = total_meses.where(total_meses >= 0, other = pd.NA)

        df['antiguedad_total_meses'] = total_meses

        df['rango_antiguedad_meses'] = _bin_numeric_series(
            series_in = df['antiguedad_total_meses'],
            step = int(antiguedad_step),
            start_value = 0,
            no_spec_label = 'No especificado',
            min_value_allowed = 0,
        ).fillna('No especificado')
    else:
        df['antiguedad_total_meses'] = pd.NA
        df['rango_antiguedad_meses'] = 'No especificado'

    return df


# 18. Función principal: construir tablas de reporte (solo reportes; asume df ya preparado)
# Modificación: filtros aceptan valor único o lista/tuple/set

def build_site_report_tables(
    df_in,
    site_name = None,                # None, str, o lista de str
    sexo = None,                     # None, str, o lista de str
    rango_edad = None,               # None, str, o lista de str
    rango_antiguedad_meses = None,   # None, str, o lista de str
):
    # 18.1 Helper: convertir filtro a lista (o None)
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

    # 18.2 Helper: normalizar etiqueta de site
    def _site_label(x):
        s = _normalize_str_or_na(x)
        if pd.isna(s):
            return 'No especificado'
        return s

    # 18.3 Helper: construir cada bloque de reporte para un df_part
    def _make_header_row(df_part, site_label):
        n_colab = len(df_part)
        prom_final = df_part['count_final'].mean()
        med_final = df_part['count_final'].median()

        level_raw = classify_score(prom_final, TH_FINAL['final'])
        level_disp = RISK_DISPLAY.get(level_raw, level_raw)

        return {
            'site': site_label,
            'num_colaboradores': n_colab,
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
        # Asume df ya preparado: sexo_norm, rango_edad, rango_antiguedad_meses
        if 'sexo_norm' in df_part.columns:
            df_demo_sexo = _build_dist_table(
                series_in = df_part['sexo_norm'],
                label_col = 'sexo',
                no_spec_label = 'No especificado',
                order = ['Femenino', 'Masculino', 'No binario', 'Otro', 'No especificado'],
            )
        else:
            df_demo_sexo = pd.DataFrame(columns = ['sexo', 'cantidad_colaboradores', 'porcentaje'])

        if 'rango_edad' in df_part.columns:
            df_demo_edad = _build_dist_table(
                series_in = df_part['rango_edad'],
                label_col = 'rango_edad',
                no_spec_label = 'No especificado',
            )
        else:
            df_demo_edad = pd.DataFrame(columns = ['rango_edad', 'cantidad_colaboradores', 'porcentaje'])

        if 'rango_antiguedad_meses' in df_part.columns:
            df_demo_ant = _build_dist_table(
                series_in = df_part['rango_antiguedad_meses'],
                label_col = 'rango_antiguedad_meses',
                no_spec_label = 'No especificado',
            )
        else:
            df_demo_ant = pd.DataFrame(columns = ['rango_antiguedad_meses', 'cantidad_colaboradores', 'porcentaje'])

        df_demo_sexo.insert(0, 'site', site_label) if not df_demo_sexo.empty else None
        df_demo_edad.insert(0, 'site', site_label) if not df_demo_edad.empty else None
        df_demo_ant.insert(0, 'site', site_label) if not df_demo_ant.empty else None

        if df_demo_sexo.empty:
            df_demo_sexo = pd.DataFrame(columns = ['site', 'sexo', 'cantidad_colaboradores', 'porcentaje'])

        if df_demo_edad.empty:
            df_demo_edad = pd.DataFrame(columns = ['site', 'rango_edad', 'cantidad_colaboradores', 'porcentaje'])

        if df_demo_ant.empty:
            df_demo_ant = pd.DataFrame(columns = ['site', 'rango_antiguedad_meses', 'cantidad_colaboradores', 'porcentaje'])

        return df_demo_sexo, df_demo_edad, df_demo_ant

    # 18.4 Normalizar filtros
    sites_filter = _as_list(site_name)
    sexo_filter = _as_list(sexo)
    edad_filter = _as_list(rango_edad)
    ant_filter = _as_list(rango_antiguedad_meses)

    # 18.5 Construir scope base por sites
    if sites_filter is None:
        df_scope = df_in.copy()
        include_general = True
    else:
        if 'site' not in df_in.columns:
            raise ValueError('La columna "site" no existe en el dataframe de entrada.')
        df_scope = df_in[df_in['site'].isin(sites_filter)].copy()
        include_general = len(sites_filter) > 1  # regla: si es un solo site, no duplicar

    if df_scope.empty:
        raise ValueError('No se encontraron registros con el filtro de site.')

    # 18.6 Aplicar filtros demográficos (sobre el scope)
    if sexo_filter is not None:
        if 'sexo_norm' not in df_scope.columns:
            raise ValueError('Falta la columna "sexo_norm". Primero ejecuta prepare_nom35_dataframe().')
        df_scope = df_scope[df_scope['sexo_norm'].isin(sexo_filter)].copy()

    if edad_filter is not None:
        if 'rango_edad' not in df_scope.columns:
            raise ValueError('Falta la columna "rango_edad". Primero ejecuta prepare_nom35_dataframe().')
        df_scope = df_scope[df_scope['rango_edad'].isin(edad_filter)].copy()

    if ant_filter is not None:
        if 'rango_antiguedad_meses' not in df_scope.columns:
            raise ValueError('Falta la columna "rango_antiguedad_meses". Primero ejecuta prepare_nom35_dataframe().')
        df_scope = df_scope[df_scope['rango_antiguedad_meses'].isin(ant_filter)].copy()

    if df_scope.empty:
        raise ValueError(
            f'No se encontraron registros con los filtros: '
            f'site = {sites_filter}, sexo = {sexo_filter}, rango_edad = {edad_filter}, rango_antiguedad_meses = {ant_filter}'
        )

    # 18.7 Salidas acumuladas (por site + GENERAL condicional)
    headers = []
    cats = []
    doms = []
    dists = []
    demos_sexo = []
    demos_edad = []
    demos_ant = []

    if 'site' not in df_scope.columns:
        # Sin site: todo se trata como un único bloque
        site_lab = 'GENERAL'
        headers.append(_make_header_row(df_scope, site_lab))
        cats.append(_make_cat_table(df_scope, site_lab))
        doms.append(_make_dom_table(df_scope, site_lab))
        dists.append(_make_dist_final(df_scope, site_lab))

        ds, de, da = _make_demo_tables(df_scope, site_lab)
        demos_sexo.append(ds)
        demos_edad.append(de)
        demos_ant.append(da)

        include_general = False
    else:
        # Ordenar sites dentro del scope real (evita problemas de mapeo/NA)
        sites_present = df_scope['site'].dropna().astype(str).unique().tolist()
        sites_present = sorted(sites_present)

        # Si hay NA en site, lo agregamos al final como "No especificado"
        has_na_site = df_scope['site'].isna().any()

        for s in sites_present:
            df_part = df_scope[df_scope['site'].astype(str) == s].copy()
            if df_part.empty:
                continue

            s_lab = _site_label(s)
            headers.append(_make_header_row(df_part, s_lab))
            cats.append(_make_cat_table(df_part, s_lab))
            doms.append(_make_dom_table(df_part, s_lab))
            dists.append(_make_dist_final(df_part, s_lab))

            ds, de, da = _make_demo_tables(df_part, s_lab)
            demos_sexo.append(ds)
            demos_edad.append(de)
            demos_ant.append(da)

        if has_na_site:
            df_part = df_scope[df_scope['site'].isna()].copy()
            if not df_part.empty:
                s_lab = 'No especificado'
                headers.append(_make_header_row(df_part, s_lab))
                cats.append(_make_cat_table(df_part, s_lab))
                doms.append(_make_dom_table(df_part, s_lab))
                dists.append(_make_dist_final(df_part, s_lab))

                ds, de, da = _make_demo_tables(df_part, s_lab)
                demos_sexo.append(ds)
                demos_edad.append(de)
                demos_ant.append(da)

        # GENERAL (sobre todo el scope filtrado) sólo si aplica la regla
        if include_general:
            g_lab = 'GENERAL'
            headers.append(_make_header_row(df_scope, g_lab))
            cats.append(_make_cat_table(df_scope, g_lab))
            doms.append(_make_dom_table(df_scope, g_lab))
            dists.append(_make_dist_final(df_scope, g_lab))

            ds, de, da = _make_demo_tables(df_scope, g_lab)
            demos_sexo.append(ds)
            demos_edad.append(de)
            demos_ant.append(da)

    # 18.8 Concatenar salidas
    df_header = pd.DataFrame(headers)

    df_cat = pd.concat(cats, ignore_index = True) if cats else pd.DataFrame(
        columns = ['site', 'categoria_clave', 'categoria', 'calificacion_promedio', 'calificacion_mediana', 'nivel_riesgo']
    )

    df_dom = pd.concat(doms, ignore_index = True) if doms else pd.DataFrame(
        columns = ['site', 'dominio_clave', 'dominio', 'dimension', 'calificacion_promedio', 'calificacion_mediana', 'nivel_riesgo']
    )

    df_dist = pd.concat(dists, ignore_index = True) if dists else pd.DataFrame(
        columns = ['site', 'nivel_riesgo', 'cantidad_colaboradores']
    )

    df_demo_sexo = pd.concat(demos_sexo, ignore_index = True) if demos_sexo else pd.DataFrame(
        columns = ['site', 'sexo', 'cantidad_colaboradores', 'porcentaje']
    )

    df_demo_edad = pd.concat(demos_edad, ignore_index = True) if demos_edad else pd.DataFrame(
        columns = ['site', 'rango_edad', 'cantidad_colaboradores', 'porcentaje']
    )

    df_demo_antiguedad = pd.concat(demos_ant, ignore_index = True) if demos_ant else pd.DataFrame(
        columns = ['site', 'rango_antiguedad_meses', 'cantidad_colaboradores', 'porcentaje']
    )

    # 18.9 Ordenar GENERAL al final en todos
    def _sort_general_last(df, site_col = 'site'):
        if df.empty or site_col not in df.columns:
            return df
        df = df.copy()
        df['_ord'] = df[site_col].map(lambda x: 1 if x == 'GENERAL' else 0)
        df = df.sort_values(['_ord', site_col]).drop(columns = ['_ord']).reset_index(drop = True)
        return df

    df_header = _sort_general_last(df_header, 'site')
    df_cat = _sort_general_last(df_cat, 'site')
    df_dom = _sort_general_last(df_dom, 'site')
    df_dist = _sort_general_last(df_dist, 'site')
    df_demo_sexo = _sort_general_last(df_demo_sexo, 'site')
    df_demo_edad = _sort_general_last(df_demo_edad, 'site')
    df_demo_antiguedad = _sort_general_last(df_demo_antiguedad, 'site')

    # 18.10 SANITY FIX: si include_general es False, eliminar cualquier GENERAL que haya quedado por error
    # (Esto corrige el caso que mencionas: un solo site pero aparece GENERAL en df_demo_antiguedad)
    if not include_general:
        df_header = df_header[df_header['site'] != 'GENERAL'].copy()
        df_cat = df_cat[df_cat['site'] != 'GENERAL'].copy()
        df_dom = df_dom[df_dom['site'] != 'GENERAL'].copy()
        df_dist = df_dist[df_dist['site'] != 'GENERAL'].copy()
        df_demo_sexo = df_demo_sexo[df_demo_sexo['site'] != 'GENERAL'].copy()
        df_demo_edad = df_demo_edad[df_demo_edad['site'] != 'GENERAL'].copy()
        df_demo_antiguedad = df_demo_antiguedad[df_demo_antiguedad['site'] != 'GENERAL'].copy()

    return (
        df_header.reset_index(drop = True),
        df_cat.reset_index(drop = True),
        df_dom.reset_index(drop = True),
        df_dist.reset_index(drop = True),
        df_demo_sexo.reset_index(drop = True),
        df_demo_edad.reset_index(drop = True),
        df_demo_antiguedad.reset_index(drop = True),
    )

# 19. Uso típico:
# df_prepared = prepare_nom35_dataframe(nom35_classified_df, edad_step = 5, antiguedad_step = 5)
# out = build_site_report_tables(df_prepared, site_name = 'EMPECO C', sexo = 'Masculino', rango_edad = '18-20', rango_antiguedad_meses = '0-5')
nom35_final = prepare_nom35_dataframe(nom35_classified_df)
print(sorted(nom35_final.site.unique()))
print(sorted(nom35_final.sexo_norm.unique()))
print(sorted(nom35_final.rango_edad.unique()))
print(sorted(nom35_final.rango_antiguedad_meses.unique()))
df_header, df_cat, df_dom, df_dist, df_demo_sexo, df_demo_edad, df_demo_antiguedad = build_site_report_tables(
    nom35_final,
    'EMPECO C'
)

df_header
df_cat
df_dom
df_dist
df_demo_sexo
df_demo_edad
df_demo_antiguedad


nom35_classified_df.to_excel(r'C:\Users\sebastian.cadena_kav\Documents\nom35\nom35\outputs\nom35_classified_df.xlsx', index = False)
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
