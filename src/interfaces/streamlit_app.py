# Aplicación Streamlit para Once Noticias - Sistema Optimizado
import os
import sys

# Asegurar que el directorio raíz está en el path
if os.path.abspath('.') not in sys.path:
    sys.path.insert(0, os.path.abspath('.'))

import streamlit as st
import openai
from datetime import datetime
from typing import Dict, Any
import json

# Librerías para exportación
try:
    from docx import Document
    from docx.shared import Inches
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    import io
    EXPORT_AVAILABLE = True
except ImportError:
    EXPORT_AVAILABLE = False

# Importaciones del sistema optimizado
from src.core.prompt_system import OptimizedOnceNoticiasPromptSystem
from src.core.quality_assurance import OnceNoticiasQualityAssurance
from config.settings import config

# Configuración de la página
st.set_page_config(
    page_title=config.STREAMLIT_CONFIG["page_title"],
    page_icon=config.STREAMLIT_CONFIG["page_icon"],
    layout=config.STREAMLIT_CONFIG["layout"],
    initial_sidebar_state="collapsed"  # Sidebar sin contenido
)

def get_web_search_setting():
    """Determina la configuración de force_web_search basada en la selección actual"""
    web_search_mode = st.session_state.get('web_search_mode', '🤖 Auto (recomendado)')

    if web_search_mode == "🌐 Siempre activada":
        return True
    elif web_search_mode == "📚 Solo conocimiento base":
        return False
    else:  # Auto (recomendado)
        return None

def initialize_system():
    """Inicializa el sistema editorial optimizado"""

    # Configurar OpenAI
    openai_api_key = config.get_api_key("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("❌ OPENAI_API_KEY no configurada. Configúrala en config/.streamlit/secrets.toml")
        st.stop()

    openai.api_key = openai_api_key
    client = openai.OpenAI(api_key=openai_api_key)

    # Inicializar sistemas (sin forzar base de datos)
    prompt_system = OptimizedOnceNoticiasPromptSystem(client, enable_database=None)
    qa_system = OnceNoticiasQualityAssurance()

    return prompt_system, qa_system

def display_content_with_citations(content: str, citations: list, user_sources: str = ""):
    """
    Muestra contenido con citaciones inline clickeables y fuentes del usuario
    """
    if not citations and not user_sources:
        st.markdown(content)
        return

    # Mostrar contenido principal
    st.markdown(content)

    # Mostrar fuentes si hay citaciones o fuentes del usuario
    if citations or user_sources:
        st.markdown("---")
        st.markdown("### 📚 Fuentes consultadas:")

        citation_count = 0

        # Mostrar citaciones de web search si las hay
        if citations:
            # Agrupar citaciones únicas por URL
            unique_citations = {}
            for citation in citations:
                url = citation.get('url', '')

                if url and url not in unique_citations:
                    # Actualizar citation con URL limpia
                    citation_copy = citation.copy()
                    citation_copy['url'] = url
                    unique_citations[url] = citation_copy

            # Mostrar cada fuente con formato mejorado
            for i, (url, citation) in enumerate(unique_citations.items(), 1):
                title = citation.get('title', 'Fuente sin título')

                # Acortar títulos muy largos
                if len(title) > 80:
                    title = title[:77] + "..."

                # Crear tarjeta de citación
                st.markdown(f"""
                **{i}.** [{title}]({url})
                """)
                citation_count = i

        # Mostrar fuentes del usuario si las hay
        if user_sources and user_sources.strip():
            st.markdown("#### 📝 Fuentes proporcionadas por el usuario:")

            # Procesar fuentes del usuario línea por línea
            sources_lines = [line.strip() for line in user_sources.split('\n') if line.strip()]
            for i, source in enumerate(sources_lines, citation_count + 1):
                # Detectar si es un URL
                if source.startswith('http'):
                    st.markdown(f"**{i}.** [{source}]({source})")
                else:
                    st.markdown(f"**{i}.** {source}")

        # Mensaje final
        total_sources = len(citations) if citations else 0
        user_sources_count = len([line for line in user_sources.split('\n') if line.strip()]) if user_sources else 0

        if total_sources > 0 and user_sources_count > 0:
            st.markdown(f"*{total_sources} fuente(s) automática(s) + {user_sources_count} del usuario*")
        elif total_sources > 0:
            st.markdown(f"*{total_sources} fuente(s) consultada(s) automáticamente*")
        elif user_sources_count > 0:
            st.markdown(f"*{user_sources_count} fuente(s) proporcionada(s) por el usuario*")

def create_word_document(content: str, metadata: Dict) -> io.BytesIO:
    """Crea un documento Word con el contenido generado"""
    if not EXPORT_AVAILABLE:
        return None

    doc = Document()

    # Agregar encabezado Once Noticias
    header = doc.sections[0].header
    header_para = header.paragraphs[0]
    header_para.text = "Once Noticias - Sistema Editorial Optimizado"

    # Título del documento
    title = doc.add_heading('Once Noticias', 0)
    title.alignment = 1  # Centrado

    # Metadatos
    doc.add_heading('Información del Contenido', level=2)
    info_para = doc.add_paragraph()
    info_para.add_run(f"Categoría: ").bold = True
    info_para.add_run(f"{metadata.get('category', '')} / {metadata.get('subcategory', '')}\n")
    info_para.add_run(f"Tipo: ").bold = True
    info_para.add_run(f"{metadata.get('text_type', '')}\n")
    info_para.add_run(f"Fecha: ").bold = True
    info_para.add_run(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    info_para.add_run(f"Calidad: ").bold = True
    info_para.add_run(f"{metadata.get('quality_score', 0)}%\n")
    info_para.add_run(f"Tokens: ").bold = True
    info_para.add_run(f"{metadata.get('token_count', 0):,}")

    # Separador
    doc.add_page_break()

    # Contenido principal
    doc.add_heading('Contenido Generado', level=1)

    # Agregar contenido párrafo por párrafo
    for paragraph in content.split('\n\n'):
        if paragraph.strip():
            doc.add_paragraph(paragraph.strip())

    # Pie de página
    footer = doc.sections[0].footer
    footer_para = footer.paragraphs[0]
    footer_para.text = f"Generado por Once Noticias AI - {datetime.now().strftime('%d/%m/%Y')}"

    # Guardar en BytesIO
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def create_pdf_document(content: str, metadata: Dict) -> io.BytesIO:
    """Crea un documento PDF con el contenido generado"""
    if not EXPORT_AVAILABLE:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Crear estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1,  # Centrado
        spaceAfter=30
    )

    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12
    )

    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=0  # Justificado
    )

    metadata_style = ParagraphStyle(
        'Metadata',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )

    # Contenido del PDF
    story = []

    # Título
    story.append(Paragraph("Once Noticias", title_style))
    story.append(Paragraph("Sistema Editorial Optimizado", header_style))
    story.append(Spacer(1, 20))

    # Metadatos
    story.append(Paragraph("Información del Contenido", header_style))
    story.append(Paragraph(f"<b>Categoría:</b> {metadata.get('category', '')} / {metadata.get('subcategory', '')}", metadata_style))
    story.append(Paragraph(f"<b>Tipo:</b> {metadata.get('text_type', '')}", metadata_style))
    story.append(Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", metadata_style))
    story.append(Paragraph(f"<b>Calidad:</b> {metadata.get('quality_score', 0)}%", metadata_style))
    story.append(Paragraph(f"<b>Tokens:</b> {metadata.get('token_count', 0):,}", metadata_style))
    story.append(Spacer(1, 30))

    # Contenido principal
    story.append(Paragraph("Contenido Generado", header_style))
    story.append(Spacer(1, 12))

    # Agregar contenido párrafo por párrafo
    for paragraph in content.split('\n\n'):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), content_style))

    # Pie de página
    story.append(Spacer(1, 50))
    story.append(Paragraph(f"Generado por Once Noticias AI - {datetime.now().strftime('%d/%m/%Y')}", metadata_style))

    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    """Función principal de la aplicación"""

    # Inicializar sistemas
    prompt_system, qa_system = initialize_system()

    # Título principal
    st.title("📰 Once Noticias - Sistema Editorial Optimizado")
    st.markdown("*Reducción de 60% en tokens • Mayor velocidad • Calidad mejorada*")

    # Configuración del contenido
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎯 Configuración del Contenido")

        # Selección de parámetros
        category = st.selectbox(
            "Categoría",
            config.CATEGORIES,
            index=1  # Economía por defecto
        )

        subcategory = st.selectbox(
            "Subcategoría",
            config.SUBCATEGORIES,
            index=1  # Finanzas por defecto
        )

        text_type = st.selectbox(
            "Tipo de Texto",
            config.TEXT_TYPES,
            index=0  # Nota Periodística por defecto
        )

        # Selección de longitud
        length_option = st.selectbox(
            "Longitud del Contenido",
            list(config.LENGTH_OPTIONS.keys()),
            index=0  # Auto por defecto
        )
        selected_length = config.LENGTH_OPTIONS[length_option]

    with col2:
        st.subheader("⚙️ Configuración Avanzada")

        # Control de búsqueda web
        web_search_mode = st.selectbox(
            "🔍 Búsqueda Web",
            ["🤖 Auto (recomendado)", "🌐 Siempre activada", "📚 Solo conocimiento base"],
            index=0,
            help="Auto: usa web search cuando sea necesario. Siempre: búsqueda web en cada generación. Solo base: sin búsqueda web."
        )

        # Guardar configuración en session_state para persistencia
        st.session_state.web_search_mode = web_search_mode

        # Mostrar configuración de almacenamiento
        storage_info = prompt_system.get_storage_status()
        st.info(f"📁 {storage_info['status']}")

        # Opción para cambiar modo de almacenamiento
        if st.button("🔄 Cambiar Almacenamiento"):
            st.session_state.show_storage_config = not st.session_state.get('show_storage_config', False)

    # Configuración de almacenamiento expandible
    if st.session_state.get('show_storage_config', False):
        with st.expander("🗄️ Configuración de Almacenamiento", expanded=True):
            storage_mode = st.radio(
                "Modo de Almacenamiento",
                ["Solo Local", "Solo Snowflake (si está configurado)", "Ambos"],
                index=0
            )

            if storage_mode == "Solo Snowflake (si está configurado)":
                if not config.is_database_available():
                    st.warning("⚠️ Snowflake no está configurado. Se usará almacenamiento local.")
                else:
                    st.success("✅ Snowflake disponible")

            st.info("💡 El almacenamiento local siempre está disponible como respaldo")

    # Input principal
    st.subheader("✍️ Solicitud Editorial")
    user_prompt = st.text_area(
        "Describe el contenido que necesitas generar:",
        height=100,
        placeholder="Ejemplo: Análisis del impacto de las nuevas políticas comerciales en el sector energético mexicano..."
    )

    # ✅ NUEVO: Campo para fuentes y referencias
    st.subheader("📚 Fuentes y Referencias (Opcional)")
    user_sources = st.text_area(
        "Comparte fuentes, links, datos o referencias específicas:",
        height=80,
        placeholder="Ejemplo: Reporte INEGI 2024, https://example.com/data, cifras del Banco de México, estudio de la UNAM sobre energías renovables...",
        help="Estas fuentes se integrarán al contenido junto con la búsqueda web automática"
    )

    # Botón de generación
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "🚀 Generar Contenido Optimizado",
            type="primary",
            use_container_width=True
        )

    # Procesamiento de la solicitud
    if generate_button and user_prompt:

        with st.spinner("🔄 Generando contenido optimizado..."):

            try:
                # Determinar si usar Web Search basado en la selección del usuario
                force_web_search = get_web_search_setting()

                # Generar contenido con Web Search
                content_data = prompt_system.generate_content_with_web_search(
                    category=category,
                    subcategory=subcategory,
                    text_type=text_type,
                    user_prompt=user_prompt,
                    sources=user_sources,
                    selected_length=selected_length,
                    force_web_search=force_web_search
                )

                generated_content = content_data.get("content", "")
                token_count = content_data.get("token_count", 0)
                citations = content_data.get("citations", [])
                web_search_used = content_data.get("web_search_used", False)

                # Guardar en session_state para flujo iterativo
                st.session_state.current_content = generated_content
                st.session_state.current_metadata = {
                    "user_prompt": user_prompt,
                    "user_sources": user_sources,  # ✅ Guardar fuentes del usuario
                    "category": category,
                    "subcategory": subcategory,
                    "text_type": text_type,
                    "token_count": token_count,
                    "length_setting": selected_length,
                    "citations": citations,
                    "web_search_used": web_search_used
                }
                st.session_state.iteration_count = 1

                # ✅ NUEVO: Inicializar historial de iteraciones
                st.session_state.iteration_history = {
                    1: {
                        "content": generated_content,
                        "metadata": st.session_state.current_metadata.copy(),
                        "timestamp": datetime.now().isoformat(),
                        "feedback_applied": "Contenido inicial",
                        "web_search_config": st.session_state.get('web_search_mode', '🤖 Auto (recomendado)')
                    }
                }
                st.session_state.current_iteration = 1

                # Mostrar solo éxito (el contenido se mostrará en la sección "Contenido Actual")
                if web_search_used:
                    st.success("✅ Contenido generado exitosamente con información actualizada de la web")
                else:
                    st.success("✅ Contenido generado exitosamente")
                st.info("📄 Ve abajo para ver tu contenido y poder mejorarlo iterativamente")

            except Exception as e:
                st.error(f"❌ Error al generar contenido: {str(e)}")
                st.error("Verifica tu configuración de OpenAI y conexión a internet")

    elif generate_button and not user_prompt:
        st.warning("⚠️ Por favor, ingresa una solicitud editorial")

    # ===== SECCIÓN DE CONTENIDO ACTUAL Y MEJORA ITERATIVA =====
    if hasattr(st.session_state, 'current_content') and st.session_state.current_content:

        # Contenedor para scroll automático
        content_container = st.container()

        with content_container:
            st.markdown("---")

            # ✅ SELECTOR DE ITERACIONES
            if hasattr(st.session_state, 'iteration_history') and len(st.session_state.iteration_history) > 1:
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.subheader("📄 Contenido Actual")

                with col2:
                    # Selector de iteración más compacto
                    available_iterations = list(st.session_state.iteration_history.keys())
                    current_iteration = st.session_state.get('current_iteration', max(available_iterations))

                    # Formato más compacto
                    col2a, col2b = st.columns([1, 1])
                    with col2a:
                        selected_iteration = st.selectbox(
                            "Ver versión:",
                            available_iterations,
                            index=available_iterations.index(current_iteration),
                            key="iteration_selector",
                            format_func=lambda x: f"#{x}"
                        )

                    with col2b:
                        st.markdown(f"<small style='color: #666; margin-top: 24px; display: block;'>de {len(available_iterations)} total</small>", unsafe_allow_html=True)

                    # Actualizar iteración actual si cambió
                    if selected_iteration != st.session_state.get('current_iteration'):
                        st.session_state.current_iteration = selected_iteration
                        # Cargar contenido de la iteración seleccionada
                        selected_data = st.session_state.iteration_history[selected_iteration]
                        st.session_state.current_content = selected_data["content"]
                        st.session_state.current_metadata = selected_data["metadata"]
                        st.rerun()

                with col3:
                    # Mostrar timestamp de la iteración actual
                    current_iter_data = st.session_state.iteration_history[selected_iteration]
                    timestamp = current_iter_data.get("timestamp", "")
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            time_str = dt.strftime("%H:%M")
                            st.markdown(f"<small style='color: #666; margin-top: 24px; display: block;'>{time_str}</small>", unsafe_allow_html=True)
                        except:
                            pass

                # Mostrar información de la iteración seleccionada
                current_iter_data = st.session_state.iteration_history[selected_iteration]
                feedback_info = current_iter_data.get("feedback_applied", "")
                web_config = current_iter_data.get("web_search_config", "")

                if feedback_info and feedback_info != "Contenido inicial":
                    display_info = f"💬 **Mejora aplicada:** {feedback_info[:100]}..."
                    if web_config:
                        mode_short = {
                            '🤖 Auto (recomendado)': 'Auto',
                            '🌐 Siempre activada': 'Siempre Web',
                            '📚 Solo conocimiento base': 'Solo Base'
                        }.get(web_config, 'Auto')
                        display_info += f" | **Config:** {mode_short}"
                    st.info(display_info)

            else:
                # Título y iteración en la misma línea (caso original)
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.subheader("📄 Contenido Actual")
                with col2:
                    st.metric("Iteración", f"#{st.session_state.get('iteration_count', 1)}", label_visibility="collapsed")

            # Mostrar información del contenido
            current_metadata = st.session_state.current_metadata
            info_text = f"**{current_metadata.get('category', '')} / {current_metadata.get('subcategory', '')}** • **{current_metadata.get('text_type', '')}**"

            # Agregar indicador de Web Search si se usó
            if current_metadata.get('web_search_used', False):
                num_sources = len(current_metadata.get('citations', []))
                if num_sources > 0:
                    info_text += f" • 🌐 **Información actualizada ({num_sources} fuentes)**"
                else:
                    info_text += " • 🌐 **Con búsqueda web**"
            else:
                info_text += " • 📚 **Solo conocimiento base**"

            # Agregar indicador de fuentes del usuario
            user_sources = current_metadata.get('user_sources', '')
            if user_sources and user_sources.strip():
                info_text += " • 📝 **Con fuentes del usuario**"

            # Agregar configuración actual de búsqueda web
            current_web_mode = st.session_state.get('web_search_mode', '🤖 Auto (recomendado)')
            mode_short = {
                '🤖 Auto (recomendado)': 'Auto',
                '🌐 Siempre activada': 'Siempre Web',
                '📚 Solo conocimiento base': 'Solo Base'
            }.get(current_web_mode, 'Auto')
            info_text += f" • **Config: {mode_short}**"

            st.markdown(info_text)

            st.markdown("---")

            # Mostrar contenido actual con citaciones
            citations = current_metadata.get('citations', [])
            display_content_with_citations(st.session_state.current_content, citations, user_sources)

            # Botones de descarga (solo Word y PDF)
            st.markdown("---")
            col1, col2 = st.columns(2)

            iteration = st.session_state.get('iteration_count', 1)

            # Word
            with col1:
                if EXPORT_AVAILABLE:
                    word_doc = create_word_document(st.session_state.current_content, current_metadata)
                    if word_doc:
                        st.download_button(
                            label="📄 Descargar Word",
                            data=word_doc,
                            file_name=f"contenido_{current_metadata.get('category', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"download_word_iter_{iteration}",
                            use_container_width=True
                        )
                else:
                    st.button("📄 Word (No disponible)", disabled=True, key=f"word_disabled_iter_{iteration}", use_container_width=True)

            # PDF
            with col2:
                if EXPORT_AVAILABLE:
                    pdf_doc = create_pdf_document(st.session_state.current_content, current_metadata)
                    if pdf_doc:
                        st.download_button(
                            label="📑 Descargar PDF",
                            data=pdf_doc,
                            file_name=f"contenido_{current_metadata.get('category', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            key=f"download_pdf_iter_{iteration}",
                            use_container_width=True
                        )
                else:
                    st.button("📑 PDF (No disponible)", disabled=True, key=f"pdf_disabled_iter_{iteration}", use_container_width=True)

        # ===== SECCIÓN DE FEEDBACK (SOLO SI NO ESTÁ PROCESANDO) =====
        if not st.session_state.get('processing_improvement', False):
            st.markdown("---")
            st.subheader("💬 ¿Qué te pareció la nota? ¿Quisieras realizar algún ajuste?")

            # Solo el feedback, sin sugerencias
            feedback_key = f"feedback_iteration_{st.session_state.get('iteration_count', 1)}"
            user_feedback = st.text_area(
                "Comparte tu feedback específico:",
                height=100,
                placeholder="Ejemplo: El título podría ser más llamativo, agregar más datos de INEGI sobre el impacto económico, incluir cifras específicas de turistas, mencionar destinos específicos como Tulum o Puerto Escondido...",
                key=feedback_key
            )

            # Información sobre consistencia editorial
            st.info("💡 **Nota**: Las mejoras mantendrán automáticamente el tono, estilo y lineamientos editoriales de Once Noticias mientras aplican tu feedback.")

            # Botones optimizados
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                improve_button_key = f"improve_button_iter_{st.session_state.get('iteration_count', 1)}"
                if st.button("🚀 Mejorar Contenido", type="primary", use_container_width=True, key=improve_button_key):
                    if user_feedback:
                        # Marcar que estamos procesando para ocultar feedback
                        st.session_state.processing_improvement = True
                        st.rerun()
                    else:
                        st.warning("⚠️ Por favor, proporciona feedback específico para mejorar el contenido")

            with col3:
                if st.button("🗑️ Comenzar Nuevo Contenido", use_container_width=True, key=f"new_content_iter_{st.session_state.get('iteration_count', 1)}"):
                    # Limpiar session_state
                    for key in ['current_content', 'current_metadata', 'iteration_count', 'processing_improvement', 'iteration_history', 'current_iteration']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

        else:
            # Mostrar progreso y procesar mejora
            st.info("🔄 Mejorando contenido con tu feedback...")

            # Obtener el feedback del estado anterior
            feedback_key = f"feedback_iteration_{st.session_state.get('iteration_count', 1)}"
            user_feedback = st.session_state.get(feedback_key, "")

            if user_feedback:
                try:
                    # Obtener configuración de búsqueda web actual (usar la del selectbox en la UI)
                    force_web_search = get_web_search_setting()

                    # Usar el nuevo método de mejora que mantiene lineamientos Once Noticias
                    content_data = prompt_system.generate_improvement_with_web_search(
                        category=current_metadata.get('category', ''),
                        subcategory=current_metadata.get('subcategory', ''),
                        text_type=current_metadata.get('text_type', ''),
                        initial_content=st.session_state.current_content,
                        user_feedback=user_feedback,
                        sources=current_metadata.get('user_sources', ''),
                        selected_length=current_metadata.get('length_setting', 'auto'),
                        force_web_search=force_web_search
                    )

                    improved_content = content_data.get("content", "")
                    improved_tokens = content_data.get("token_count", 0)
                    improved_citations = content_data.get("citations", [])
                    improved_web_search_used = content_data.get("web_search_used", False)

                    # Actualizar session_state con el contenido mejorado
                    st.session_state.current_content = improved_content
                    st.session_state.current_metadata.update({
                        "token_count": improved_tokens,
                        "last_feedback": user_feedback,
                        "citations": improved_citations,
                        "web_search_used": improved_web_search_used
                    })
                    st.session_state.iteration_count += 1
                    st.session_state.processing_improvement = False

                    # ✅ NUEVO: Guardar nueva iteración en historial
                    new_iteration = st.session_state.iteration_count
                    st.session_state.iteration_history[new_iteration] = {
                        "content": improved_content,
                        "metadata": st.session_state.current_metadata.copy(),
                        "timestamp": datetime.now().isoformat(),
                        "feedback_applied": user_feedback[:200],  # Primeros 200 chars del feedback
                        "web_search_config": st.session_state.get('web_search_mode', '🤖 Auto (recomendado)')
                    }
                    st.session_state.current_iteration = new_iteration

                    if improved_web_search_used:
                        st.success("✅ Contenido mejorado exitosamente con información actualizada")
                    else:
                        st.success("✅ Contenido mejorado exitosamente")

                    st.rerun()

                except Exception as e:
                    st.session_state.processing_improvement = False
                    st.error(f"❌ Error al mejorar contenido: {str(e)}")
                    st.rerun()

if __name__ == "__main__":
    main()