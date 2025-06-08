# Guía de Integración Inmediata - Mejoras Once Noticias
# Este archivo muestra los cambios exactos para app.py

"""
PASO 1: Importar los nuevos sistemas
Agregar al inicio de app.py:
"""

# Nuevas importaciones
from enhanced_prompt_system import OnceNoticiasPromptSystem
from quality_assurance_system import OnceNoticiasQualityAssurance
from research_system import OnceNoticiasResearchSystem

"""
PASO 2: Inicializar sistemas mejorados
Reemplazar la inicialización básica con:
"""

# Sistemas mejorados Once Noticias
@st.cache_resource
def initialize_once_noticias_systems():
    """Inicializa los sistemas optimizados para Once Noticias"""
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Sistema de prompts específico Once Noticias
    prompt_system = OnceNoticiasPromptSystem(client)

    # Sistema de evaluación de calidad
    quality_system = OnceNoticiasQualityAssurance()

    # Sistema de investigación (APIs opcionales por ahora)
    research_system = OnceNoticiasResearchSystem({
        "news_api": st.secrets.get("NEWS_API_KEY", ""),
        "banxico_api": st.secrets.get("BANXICO_API_KEY", "")
    })

    return prompt_system, quality_system, research_system

# Inicializar sistemas
prompt_system, quality_system, research_system = initialize_once_noticias_systems()

"""
PASO 3: Mejorar la función de generación principal
Reemplazar la función generate_content actual con:
"""

def generate_enhanced_content(user_prompt, sources_prompt, category, subcategory, text_type, selected_length="auto"):
    """
    Generación mejorada con evaluación de calidad Once Noticias y control de longitud
    """
    try:
        # Logging del intento de generación
        st.info("🔄 Generando contenido con estándares Once Noticias...")

        with st.spinner("Investigando fuentes y datos relevantes..."):
            # Pre-investigación opcional (si están disponibles las APIs)
            research_data = research_system.quick_research(
                topic=user_prompt,
                category=category,
                subcategory=subcategory
            )

        with st.spinner("Creando contenido periodístico especializado..."):
            # Crear prompt mejorado específico Once Noticias con control de longitud
            enhanced_prompt = prompt_system.create_enhanced_system_prompt(
                category=category,
                subcategory=subcategory,
                text_type=text_type,
                user_prompt=user_prompt,
                sources=sources_prompt,
                selected_length=selected_length  # Nueva funcionalidad
            )

            # Generar contenido inicial
            initial_content = call_openai_api(enhanced_prompt, user_prompt)

            if not initial_content:
                st.error("Error en la generación de contenido.")
                return None

        with st.spinner("Evaluando calidad editorial..."):
            # Evaluación de calidad específica Once Noticias
            quality_evaluation = quality_system.evaluate_content_quality(
                content=initial_content,
                metadata={
                    'category': category,
                    'subcategory': subcategory,
                    'text_type': text_type,
                    'user_prompt': user_prompt,
                    'selected_length': selected_length  # Agregar para análisis
                }
            )

            # Mostrar métricas de calidad
            display_quality_metrics(quality_evaluation)

            # Verificar si cumple estándares de publicación
            if not quality_evaluation.get("publication_ready", False):
                st.warning("⚠️ Contenido requiere mejoras. Regenerando con ajustes...")

                # Crear prompt de mejora basado en evaluación
                improvement_prompt = prompt_system.create_improvement_prompt(
                    initial_content,
                    quality_evaluation,
                    category,
                    text_type
                )

                # Regenerar con mejoras
                improved_content = call_openai_api(improvement_prompt, user_prompt)

                if improved_content:
                    # Re-evaluar contenido mejorado
                    final_evaluation = quality_system.evaluate_content_quality(
                        content=improved_content,
                        metadata={
                            'category': category,
                            'subcategory': subcategory,
                            'text_type': text_type,
                            'user_prompt': user_prompt,
                            'selected_length': selected_length
                        }
                    )

                    display_quality_metrics(final_evaluation, title="Evaluación Final")

                    return {
                        'content': improved_content,
                        'quality_evaluation': final_evaluation,
                        'research_data': research_data,
                        'improvement_applied': True,
                        'selected_length': selected_length
                    }
                else:
                    st.warning("No se pudo mejorar el contenido. Presentando versión inicial.")
                    return {
                        'content': initial_content,
                        'quality_evaluation': quality_evaluation,
                        'research_data': research_data,
                        'improvement_applied': False,
                        'selected_length': selected_length
                    }
            else:
                st.success("✅ Contenido cumple estándares de publicación Once Noticias")
                return {
                    'content': initial_content,
                    'quality_evaluation': quality_evaluation,
                    'research_data': research_data,
                    'improvement_applied': False,
                    'selected_length': selected_length
                }

    except Exception as e:
        st.error(f"Error en la generación: {str(e)}")
        return None

"""
PASO 4: Función para mostrar métricas de calidad
Agregar nueva función:
"""

def display_quality_metrics(evaluation, title="Evaluación de Calidad"):
    """Muestra las métricas de calidad de manera visual"""

    overall_score = evaluation.get("overall_score", 0)
    publication_ready = evaluation.get("publication_ready", False)

    st.subheader(title)

    # Score general
    col1, col2, col3 = st.columns(3)

    with col1:
        color = "green" if overall_score >= 85 else "orange" if overall_score >= 75 else "red"
        st.metric(
            label="Score General",
            value=f"{overall_score:.1f}/100",
            help="Evaluación general según estándares Once Noticias"
        )
        st.markdown(f"<span style='color: {color}'>{'Excelente' if overall_score >= 85 else 'Bueno' if overall_score >= 75 else 'Necesita mejoras'}</span>", unsafe_allow_html=True)

    with col2:
        st.metric(
            label="Estilo Once Noticias",
            value=f"{evaluation.get('once_noticias_compliance', {}).get('overall_style_match', 0):.1f}/100",
            help="Adherencia al estilo editorial específico de Once Noticias"
        )

    with col3:
        ready_text = "Listo ✅" if publication_ready else "Requiere mejoras ⚠️"
        st.metric(
            label="Estado",
            value=ready_text,
            help="¿Está listo para publicación según estándares editoriales?"
        )

    # Scores detallados por criterio
    if evaluation.get("detailed_scores"):
        st.subheader("Evaluación Detallada")

        criteria_names = {
            "precision_factual": "Precisión Factual",
            "calidad_periodistica": "Calidad Periodística",
            "relevancia_audiencia": "Relevancia para Audiencia",
            "completitud_informativa": "Completitud Informativa",
            "identidad_editorial": "Identidad Editorial"
        }

        for criterion, data in evaluation["detailed_scores"].items():
            score = data.get("score", 0)
            col1, col2 = st.columns([1, 3])

            with col1:
                st.metric(criteria_names.get(criterion, criterion), f"{score:.1f}/100")

            with col2:
                # Mostrar fortalezas
                if data.get("strengths"):
                    st.success("✅ " + " | ".join(data["strengths"][:2]))

                # Mostrar problemas
                if data.get("issues"):
                    st.warning("⚠️ " + " | ".join(data["issues"][:2]))

    # Recomendaciones específicas
    if evaluation.get("recommendations"):
        st.subheader("Recomendaciones de Mejora")
        for rec in evaluation["recommendations"][:5]:  # Mostrar máximo 5
            if "PRIORITY" in rec or "🔴" in rec:
                st.error(rec)
            elif "⚠️" in rec:
                st.warning(rec)
            elif "✅" in rec:
                st.success(rec)
            else:
                st.info(rec)

"""
PASO 5: Mejorar la interfaz principal con selección de longitud
En la función main(), reemplazar la generación con:
"""

def enhanced_main_interface():
    """Interfaz principal mejorada con estándares Once Noticias y control de longitud"""

    st.title("🎯 Once Noticias - Generador Inteligente")
    st.markdown("**Sistema optimizado con estándares editoriales específicos de Once Noticias**")

    # Información del sistema mejorado
    with st.expander("ℹ️ Mejoras Implementadas"):
        st.markdown("""
        **Nuevas características basadas en investigación editorial:**

        - 🎯 **Prompts especializados** por cada combinación de categoría y tipo de contenido
        - 📊 **Evaluación automática** según estándares específicos de Once Noticias
        - 🔄 **Regeneración inteligente** cuando el contenido no cumple criterios de calidad
        - 🇲🇽 **Contexto mexicano** integrado y fuentes oficiales apropiadas
        - 📝 **Patrones de atribución** característicos del medio
        - 📏 **Control de longitud** con opción "Auto" optimizada por tipo de contenido
        - ✅ **Garantía de calidad** antes de presentar contenido
        """)

    # Configuración existente (mantener igual)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Configuración")

        # Tipo de texto
        text_type = st.selectbox(
            "Tipo de contenido:",
            text_types,
            help="Cada tipo tiene patrones específicos de Once Noticias"
        )

        # Categoría principal
        selected_category = st.selectbox(
            "Categoría principal:",
            main_categories,
            help="Determina fuentes, tono y enfoque específico"
        )

        # Subcategoría
        selected_subcategory = st.selectbox(
            "Subcategoría:",
            subcategories,
            help="Especialización adicional del contenido"
        )

        # NUEVA FUNCIONALIDAD: Selección de longitud con opción Auto
        st.subheader("Longitud del Contenido")

        # Obtener opciones de longitud del sistema
        length_options = {
            "Auto (Optimizada para el tipo de contenido)": "auto",
            "Corta (100-300 palabras)": "corta",
            "Media (301-500 palabras)": "media",
            "Larga (501-800 palabras)": "larga",
            "Muy larga (801+ palabras)": "muy_larga"
        }

        selected_length_display = st.selectbox(
            "Longitud:",
            list(length_options.keys()),
            help="Selecciona 'Auto' para usar longitud optimizada según el tipo de contenido Once Noticias"
        )

        selected_length = length_options[selected_length_display]

        # Mostrar información específica cuando es Auto
        if selected_length == "auto":
            display_auto_length_info(text_type)

        # Mostrar info específica de la combinación seleccionada
        display_combination_info(text_type, selected_category)

    with col2:
        st.subheader("Contenido a generar")

        # Prompt del usuario
        user_prompt = st.text_area(
            "Tema o instrucciones:",
            placeholder="Ejemplo: Baja de la pobreza laboral según datos del INEGI...",
            height=100,
            help="Describe el tema específico que quieres cubrir"
        )

        # Fuentes y referencias
        sources_prompt = st.text_area(
            "Fuentes y referencias (opcional):",
            placeholder="URLs, nombres de fuentes, datos específicos...",
            height=80,
            help="Información adicional para enriquecer el contenido"
        )

        # Botón de generación mejorado
        if st.button("🚀 Generar Contenido Once Noticias", type="primary"):
            if user_prompt.strip():
                # Usar función de generación mejorada con longitud
                result = generate_enhanced_content(
                    user_prompt=user_prompt,
                    sources_prompt=sources_prompt,
                    category=selected_category,
                    subcategory=selected_subcategory,
                    text_type=text_type,
                    selected_length=selected_length  # Nueva funcionalidad
                )

                if result:
                    # Mostrar contenido generado
                    st.subheader("📰 Contenido Generado")

                    # Mostrar información de longitud aplicada
                    display_length_applied_info(result['selected_length'], text_type)

                    st.write(result['content'])

                    # Opciones de exportación (mantener existentes)
                    provide_download_options(result['content'], text_type)

                    # Guardar en Snowflake con evaluación de calidad
                    save_to_snowflake_enhanced(
                        user_prompt,
                        sources_prompt,
                        result['content'],
                        selected_category,
                        selected_subcategory,
                        text_type,
                        result['quality_evaluation'],
                        result['selected_length']  # Nueva información
                    )

            else:
                st.warning("Por favor, describe el tema que quieres cubrir.")

"""
PASO 6: Funciones auxiliares para la nueva funcionalidad de longitud
"""

def display_auto_length_info(text_type):
    """Muestra información sobre la longitud automática según el tipo de contenido"""

    auto_length_info = {
        "Nota Periodística": {
            "descripcion": "Breve y concisa (1-2 minutos de lectura)",
            "caracteristicas": "2-3 párrafos principales, información esencial",
            "objetivo": "Información rápida y directa según pirámide invertida"
        },
        "Artículo": {
            "descripcion": "Extenso y desarrollado (2-4 minutos de lectura)",
            "caracteristicas": "3-8 secciones temáticas, desarrollo completo",
            "objetivo": "Análisis profundo con múltiples fuentes y contexto"
        },
        "Guión de TV": {
            "descripcion": "Muy conciso (30-90 segundos de lectura)",
            "caracteristicas": "Oraciones cortas, indicaciones técnicas",
            "objetivo": "Formato optimizado para transmisión televisiva"
        },
        "Crónica": {
            "descripcion": "Variable según narrativa (sin límite fijo)",
            "caracteristicas": "Desarrollo completo de historia",
            "objetivo": "Narrativa inmersiva desde escena inicial hasta reflexión"
        }
    }

    info = auto_length_info.get(text_type, {})

    if info:
        st.info(f"""
        **Longitud Automática para {text_type}:**

        📏 **Extensión:** {info['descripcion']}
        📋 **Características:** {info['caracteristicas']}
        🎯 **Objetivo:** {info['objetivo']}
        """)

def display_length_applied_info(selected_length, text_type):
    """Muestra información sobre la longitud que se aplicó al contenido"""

    if selected_length == "auto":
        st.success(f"✅ Longitud automática aplicada - Optimizada para {text_type} según estándares Once Noticias")
    else:
        length_names = {
            "corta": "Corta (100-300 palabras)",
            "media": "Media (301-500 palabras)",
            "larga": "Larga (501-800 palabras)",
            "muy_larga": "Muy larga (801+ palabras)"
        }
        st.info(f"📏 Longitud aplicada: {length_names.get(selected_length, selected_length)}")

def display_combination_info(text_type, category):
    """Muestra información específica de la combinación seleccionada"""

    # Información específica de Once Noticias por combinación
    info_matrix = {
        ("Nota Periodística", "Economía"): {
            "estructura": "Pirámide invertida con cifras en lead",
            "fuentes": "INEGI, Banxico, SHCP",
            "elementos": "Datos + comparación temporal + impacto"
        },
        ("Artículo", "Política"): {
            "estructura": "Bloques temáticos con múltiples fuentes",
            "fuentes": "Funcionarios oficiales, comunicados",
            "elementos": "Cargos completos + equilibrio + contexto"
        },
        ("Guión de TV", "Justicia"): {
            "estructura": "Oraciones cortas + indicaciones técnicas",
            "fuentes": "FGR, autoridades policiales",
            "elementos": "Terminología precisa + evidencias + situación"
        },
        ("Crónica", "Sociedad"): {
            "estructura": "Narrativa inmersiva con personajes",
            "fuentes": "Ciudadanos, secretarías sociales",
            "elementos": "Humanización + detalles sensoriales + impacto social"
        }
        # Agregar más combinaciones según matriz del plan
    }

    combo_info = info_matrix.get((text_type, category))

    if combo_info:
        st.info(f"""
        **Patrón Once Noticias para {text_type} - {category}:**

        📐 **Estructura:** {combo_info['estructura']}
        📋 **Fuentes esperadas:** {combo_info['fuentes']}
        🎯 **Elementos clave:** {combo_info['elementos']}
        """)

"""
PASO 7: Mejorar función de guardado en Snowflake con información de longitud
"""

def save_to_snowflake_enhanced(user_prompt, sources_prompt, content, category, subcategory, text_type, quality_evaluation, selected_length):
    """Guarda en Snowflake con métricas de calidad incluidas y información de longitud"""

    try:
        conn = st.connection("snowflake")

        # Preparar datos extendidos
        data_to_save = {
            'timestamp': datetime.now(),
            'user_prompt': user_prompt,
            'sources_prompt': sources_prompt,
            'generated_content': content,
            'category': category,
            'subcategory': subcategory,
            'text_type': text_type,

            # Nueva información de longitud
            'selected_length': selected_length,
            'word_count': len(content.split()) if content else 0,

            # Métricas de calidad existentes
            'overall_quality_score': quality_evaluation.get("overall_score", 0),
            'publication_ready': quality_evaluation.get("publication_ready", False),
            'style_compliance_score': quality_evaluation.get('once_noticias_compliance', {}).get('overall_style_match', 0),

            # Scores detallados
            'precision_factual_score': quality_evaluation.get("detailed_scores", {}).get("precision_factual", {}).get("score", 0),
            'calidad_periodistica_score': quality_evaluation.get("detailed_scores", {}).get("calidad_periodistica", {}).get("score", 0),
            'relevancia_audiencia_score': quality_evaluation.get("detailed_scores", {}).get("relevancia_audiencia", {}).get("score", 0),
            'completitud_informativa_score': quality_evaluation.get("detailed_scores", {}).get("completitud_informativa", {}).get("score", 0),
            'identidad_editorial_score': quality_evaluation.get("detailed_scores", {}).get("identidad_editorial", {}).get("score", 0),

            # Metadatos adicionales
            'improvement_applied': quality_evaluation.get('improvement_applied', False),
            'recommendations_count': len(quality_evaluation.get("recommendations", [])),
            'critical_issues_count': len(quality_evaluation.get("critical_issues", []))
        }

        # Insertar con estructura extendida
        conn.execute("""
            INSERT INTO content_generation_log_enhanced
            (timestamp, user_prompt, sources_prompt, generated_content, category, subcategory, text_type,
             selected_length, word_count,
             overall_quality_score, publication_ready, style_compliance_score,
             precision_factual_score, calidad_periodistica_score, relevancia_audiencia_score,
             completitud_informativa_score, identidad_editorial_score,
             improvement_applied, recommendations_count, critical_issues_count)
            VALUES (%(timestamp)s, %(user_prompt)s, %(sources_prompt)s, %(generated_content)s,
                   %(category)s, %(subcategory)s, %(text_type)s,
                   %(selected_length)s, %(word_count)s,
                   %(overall_quality_score)s, %(publication_ready)s, %(style_compliance_score)s,
                   %(precision_factual_score)s, %(calidad_periodistica_score)s, %(relevancia_audiencia_score)s,
                   %(completitud_informativa_score)s, %(identidad_editorial_score)s,
                   %(improvement_applied)s, %(recommendations_count)s, %(critical_issues_count)s)
        """, data_to_save)

        st.success("✅ Contenido y métricas guardados correctamente")

    except Exception as e:
        st.error(f"Error al guardar: {str(e)}")

"""
PASOS ADICIONALES ACTUALIZADOS:

1. Crear tabla Snowflake extendida con campos de longitud:
```sql
CREATE TABLE content_generation_log_enhanced (
    timestamp TIMESTAMP,
    user_prompt TEXT,
    sources_prompt TEXT,
    generated_content TEXT,
    category VARCHAR(50),
    subcategory VARCHAR(50),
    text_type VARCHAR(50),
    selected_length VARCHAR(20),      -- NUEVO: auto, corta, media, larga, muy_larga
    word_count INTEGER,               -- NUEVO: conteo real de palabras
    overall_quality_score FLOAT,
    publication_ready BOOLEAN,
    style_compliance_score FLOAT,
    precision_factual_score FLOAT,
    calidad_periodistica_score FLOAT,
    relevancia_audiencia_score FLOAT,
    completitud_informativa_score FLOAT,
    identidad_editorial_score FLOAT,
    improvement_applied BOOLEAN,
    recommendations_count INTEGER,
    critical_issues_count INTEGER
);
```

2. Agregar secrets opcionales en Streamlit (sin cambios):
```toml
[secrets]
OPENAI_API_KEY = "tu_key_existente"
NEWS_API_KEY = "opcional_para_investigacion"
BANXICO_API_KEY = "opcional_para_datos_economicos"
```

3. Instalar dependencias adicionales (sin cambios):
```bash
pip install pandas numpy typing
```

CARACTERÍSTICAS NUEVAS DE LONGITUD:

✅ **Opción "Auto":** Usa longitudes optimizadas específicas por tipo de contenido Once Noticias
✅ **Control de Usuario:** Permite selección manual de longitud cuando se necesita
✅ **Información Contextual:** Muestra qué significa cada opción de longitud
✅ **Tracking de Palabras:** Cuenta y guarda palabras reales generadas
✅ **Flexibilidad:** Mantiene estructura editorial sin importar la longitud seleccionada

RESULTADO ESPERADO:
- Sistema que respeta la selección de longitud del usuario
- Opción "Auto" que optimiza longitud según tipo de contenido y estándares Once Noticias
- Interface clara que explica cada opción de longitud
- Métricas de calidad independientes de la longitud seleccionada
- Base de datos enriquecida con información de longitud para análisis posterior
"""