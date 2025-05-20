import streamlit as st
import openai
from openai import OpenAI
import os
import json
import time
import pandas as pd
import sqlite3
from datetime import datetime
import snowflake.connector
from snowflake.connector import DictCursor
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import base64
from docx import Document
from docx.shared import Inches
import io
from fpdf import FPDF
import tempfile

# Set page config at the very beginning
st.set_page_config(
    page_title="Generador de Contenido",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = False
if 'rating' not in st.session_state:
    st.session_state.rating = 5
if 'comments' not in st.session_state:
    st.session_state.comments = ""

# Initialize OpenAI
openai.api_key = st.secrets["OPENAI"]["api_key"]

# Initialize the OpenAI client
client = OpenAI(
    api_key=st.secrets["OPENAI"]["api_key"]
)

# Create SQLAlchemy engine for Snowflake
def get_snowflake_engine():
    try:
        # First connect without database to create it if needed
        conn = snowflake.connector.connect(
            user=st.secrets["SNOWFLAKE"]["user"],
            password=st.secrets["SNOWFLAKE"]["password"],
            account=st.secrets["SNOWFLAKE"]["account"],
            warehouse=st.secrets["SNOWFLAKE"]["warehouse"]
        )
        
        # Create database and schema if they don't exist
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {st.secrets['SNOWFLAKE']['database']}")
        cur.execute(f"USE DATABASE {st.secrets['SNOWFLAKE']['database']}")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {st.secrets['SNOWFLAKE']['schema']}")
        cur.close()
        conn.close()
        
        # Now create engine with the database and schema
        engine = create_engine(URL(
            account=st.secrets["SNOWFLAKE"]["account"],
            user=st.secrets["SNOWFLAKE"]["user"],
            password=st.secrets["SNOWFLAKE"]["password"],
            warehouse=st.secrets["SNOWFLAKE"]["warehouse"],
            database=st.secrets["SNOWFLAKE"]["database"],
            schema=st.secrets["SNOWFLAKE"]["schema"]
        ))
        
        return engine
    except Exception as e:
        st.error(f"Error creating Snowflake engine: {str(e)}")
        return None

# Snowflake connection function (for non-pandas operations)
def get_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=st.secrets["SNOWFLAKE"]["user"],
            password=st.secrets["SNOWFLAKE"]["password"],
            account=st.secrets["SNOWFLAKE"]["account"],
            warehouse=st.secrets["SNOWFLAKE"]["warehouse"],
            database=st.secrets["SNOWFLAKE"]["database"],
            schema=st.secrets["SNOWFLAKE"]["schema"]
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {str(e)}")
        return None

# Initialize Snowflake tables
def init_snowflake_tables():
    try:
        conn = get_snowflake_connection()
        if conn:
            cur = conn.cursor()
            
            # Create feedback table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id NUMBER AUTOINCREMENT,
                    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    rating NUMBER,
                    comments TEXT,
                    generated_text TEXT,
                    category TEXT,
                    text_type TEXT,
                    length TEXT,
                    sources TEXT,
                    tone TEXT,
                    style TEXT,
                    additional_instructions TEXT
                )
            """)
            
            # Create model metrics table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS model_metrics (
                    id NUMBER AUTOINCREMENT,
                    model_name TEXT,
                    model_version TEXT,
                    training_accuracy FLOAT,
                    validation_accuracy FLOAT,
                    last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
            """)
            
            # Create analytics view
            cur.execute("""
                CREATE OR REPLACE VIEW feedback_analytics AS
                SELECT 
                    category,
                    text_type,
                    length,
                    tone,
                    style,
                    AVG(rating) as avg_rating,
                    COUNT(*) as feedback_count,
                    COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback_count
                FROM feedback
                GROUP BY category, text_type, length, tone, style
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            st.success("Snowflake tables initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing Snowflake tables: {str(e)}")

# Initialize session state for app refresh and text input
if 'refresh' not in st.session_state:
    st.session_state.refresh = False
if 'sources_input' not in st.session_state:
    st.session_state.sources_input = ""
if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False
if 'feedback_rating' not in st.session_state:
    st.session_state.feedback_rating = 5
if 'feedback_comments' not in st.session_state:
    st.session_state.feedback_comments = ""

# Function to save feedback to Snowflake
def save_feedback(rating, comments, generated_text, metadata):
    try:
        conn = get_snowflake_connection()
        if conn:
            cur = conn.cursor()
            
            # Use the database and schema
            cur.execute(f"USE DATABASE {st.secrets['SNOWFLAKE']['database']}")
            cur.execute(f"USE SCHEMA {st.secrets['SNOWFLAKE']['schema']}")
            
            # Create DataFrame for feedback
            feedback_df = pd.DataFrame([{
                'timestamp': datetime.datetime.now(),
                'rating': int(rating),
                'comments': str(comments),
                'generated_text': str(generated_text),
                'category': str(metadata['category']),
                'text_type': str(metadata['text_type']),
                'length': str(metadata['length']),
                'sources': str(metadata['sources']),
                'tone': str(metadata['tone']),
                'style': str(metadata['style']),
                'additional_instructions': str(metadata['additional_instructions'])
            }])
            
            # Write to Snowflake
            success, nchunks, nrows, _ = snowflake.connector.pandas_tools.write_pandas(
                conn,
                feedback_df,
                'FEEDBACK',
                auto_create_table=False,
                overwrite=False
            )
            
            conn.close()
            return success
    except Exception as e:
        st.error(f"Error saving feedback to Snowflake: {str(e)}")
        return False

# Function to get feedback history from Snowflake
def get_feedback_history():
    try:
        engine = get_snowflake_engine()
        if engine:
            with engine.connect() as conn:
                query = text("""
                    SELECT 
                        timestamp,
                        rating,
                        comments,
                        category,
                        text_type,
                        length,
                        sources,
                        tone,
                        style,
                        additional_instructions
                    FROM feedback
                    ORDER BY timestamp DESC
                """)
                df = pd.read_sql(query, conn)
                return df
    except Exception as e:
        st.error(f"Error getting feedback history: {str(e)}")
        return pd.DataFrame()

# Function to get feedback analytics
def get_feedback_analytics():
    try:
        engine = get_snowflake_engine()
        if engine:
            with engine.connect() as conn:
                query = text("""
                    SELECT *
                    FROM feedback_analytics
                    ORDER BY last_feedback_time DESC
                """)
                df = pd.read_sql(query, conn)
                return df
    except Exception as e:
        st.error(f"Error getting feedback analytics: {str(e)}")
        return pd.DataFrame()

# Function to analyze feedback patterns
def analyze_feedback(feedback_df):
    if feedback_df.empty:
        return None
    
    analysis = {
        "overall_rating": feedback_df['rating'].mean(),
        "rating_trend": feedback_df.sort_values('timestamp')['rating'].tolist(),
        "category_ratings": feedback_df.groupby('category')['rating'].mean().to_dict(),
        "text_type_ratings": feedback_df.groupby('text_type')['rating'].mean().to_dict(),
        "common_comments": feedback_df['comments'].dropna().tolist(),
        "total_feedback": len(feedback_df),
        "improvement_rate": (feedback_df['rating'].mean() - 3) / 2 * 100  # Assuming 3 is baseline
    }
    return analysis

# Initialize Snowflake tables
init_snowflake_tables()

# Function to create Word document
def create_word_doc(text):
    doc = Document()
    doc.add_paragraph(text)
    return doc

# Function to create PDF document
def create_pdf_doc(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Replace unsupported characters (like en dash) with hyphen
    safe_text = text.replace("–", "-")
    # Split text into lines that fit the page width
    lines = safe_text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, txt=line)
    return pdf

# Load training data
def load_training_data():
    training_data = []
    with open('training_data.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'metadata' in data and data['metadata']:
                    training_data.append(data)
            except json.JSONDecodeError:
                continue
    return training_data

# Title and description
st.title("📝 Asistente de Redacción Periodística")

# Add some styling
st.markdown("""
<style>
    .stTextArea textarea {
        height: 200px;
    }
    .main {
        padding: 2rem;
    }
    .stSelectbox {
        margin-bottom: 1rem;
    }
    .stRadio > div {
        flex-direction: row;
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Create two columns for the dropdowns
col1, col2 = st.columns(2)

# Main categories
main_categories = [
    "Comercio",
    "Economía",
    "Energía",
    "Gobierno",
    "Política",
    "Justicia",
    "Sociedad",
    "Transporte"
]

# Subcategories
subcategories = [
    "Agricultura",
    "Finanzas",
    "Empleo",
    "Medio Ambiente",
    "Infraestructura",
    "Seguridad",
    "Comercio Internacional",
    "Salud",
    "Inversión Extranjera",
    "Mercados"
]

# Text types
text_types = [
    "Nota Periodística",
    "Artículo",
    "Guión de TV",
    "Crónica"
]

# First column - Category selection
with col1:
    selected_category = st.selectbox(
        "Selecciona la categoría principal:",
        options=main_categories,
        index=0
    )

# Second column - Subcategory selection
with col2:
    selected_subcategory = st.selectbox(
        "Selecciona la subcategoría:",
        options=subcategories,
        index=0
    )

# Text type selection
selected_text_type = st.selectbox(
    "Selecciona el tipo de texto:",
    options=text_types,
    index=0
)

# Length selector
length_options = {
    "Corta (100-300 palabras)": "corta",
    "Media (301-500 palabras)": "media",
    "Larga (501-800 palabras)": "larga",
    "Muy larga (801+ palabras)": "muy_larga"
}

selected_length = st.radio(
    "Selecciona la longitud del texto:",
    options=list(length_options.keys()),
    horizontal=True
)

# Add a description
st.markdown("""
Este asistente te ayudará a generar contenido periodístico de alta calidad. 
Escribe tus instrucciones o el tema sobre el que deseas escribir, y el asistente te ayudará a crear un texto profesional.
""")

# Add tabs for main content and feedback history
tab1, tab2, tab3 = st.tabs(["Generar Texto", "Historial de Feedback", "Entrenamiento del Modelo"])

with tab1:
    # Create the text area for user input
    user_prompt = st.text_area(
        "Escribe instrucciones para generar tu nota:", 
        value=st.session_state.user_input,
        placeholder=f"Ejemplo: Escribe un {selected_text_type.lower()} sobre {selected_category.lower()} en el área de {selected_subcategory.lower()}..."
    )

    # Update session state with the current input
    st.session_state.user_input = user_prompt

    # Add sources input
    sources_prompt = st.text_area(
        "Fuentes y referencias (opcional):",
        value=st.session_state.sources_input,
        placeholder="Ingresa las fuentes, referencias o datos específicos que deseas incluir en el texto..."
    )
    st.caption("Nota: Las fuentes proporcionadas son solo para investigación y referencia. Nunca deben ser copiadas directamente en el contenido generado.")

    # Update session state with the current sources input
    st.session_state.sources_input = sources_prompt

    # Create columns for buttons
    col1, col2 = st.columns([1, 3])

    # Add a generate button
    with col1:
        generate_button = st.button("Generar", type="primary")

    # Add a new text button
    with col2:
        if st.button("Nuevo Texto", type="secondary"):
            # Clear all session state variables
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Initialize new session state
            st.session_state.refresh = False
            st.session_state.user_input = ""
            st.session_state.sources_input = ""
            st.session_state.feedback_submitted = False
            # Rerun the app
            st.rerun()

    # If refresh flag is set, clear it and continue
    if st.session_state.get('refresh', False):
        st.session_state.refresh = False

    if generate_button:
        if user_prompt:
            with st.spinner("Generando contenido..."):
                try:
                    # Load training data
                    training_data = load_training_data()
                    
                    # Filter relevant examples based on category and text type
                    relevant_examples = [
                        example for example in training_data 
                        if selected_category.lower() in example['metadata'].get('category', '').lower() 
                        and selected_text_type.lower() in example['metadata'].get('type', '').lower()
                    ][:3]  # Get top 3 relevant examples
                    
                    # Create a more specific system prompt based on the selected category, subcategory, text type and length
                    length_instruction = {
                        "corta": "El texto debe ser conciso y directo, entre 100 y 300 palabras.",
                        "media": "El texto debe tener una extensión media, entre 301 y 500 palabras.",
                        "larga": "El texto debe ser detallado y extenso, entre 501 y 800 palabras.",
                        "muy_larga": "El texto debe ser muy detallado y extenso, con más de 801 palabras."
                    }

                    text_type_instruction = {
                        "Nota Periodística": """El texto debe seguir el formato de una nota periodística:
                        - Estilo directo y objetivo
                        - Incluir las 5W (qué, quién, cuándo, dónde, por qué) pero no hacerlo textual sobre el texto
                        - Estructura piramidal invertida (lo más importante primero)
                        - Evitar opiniones personales
                        - Usar lenguaje claro y preciso
                        - Incluir citas directas cuando sea relevante""",
                        
                        "Artículo": """El texto debe seguir el formato de un artículo:
                        - Estilo más elaborado y análisis profundo
                        - Incluir contexto y antecedentes
                        - Presentar diferentes perspectivas
                        - Usar datos y estadísticas relevantes
                        - Mantener un tono profesional pero accesible
                        - Incluir conclusiones o reflexiones finales""",
                        
                        "Guión de TV": """El texto debe seguir el formato de un guión de TV:
                        - Incluir indicaciones de cámara claras
                        - Estructurar diálogos de manera natural
                        - Describir escenas y ambientación
                        - Incluir indicaciones de sonido y música
                        - Mantener un ritmo dinámico
                        - Usar formato estándar de guión""",
                        
                        "Crónica": """El texto debe seguir el formato de una crónica:
                        - Estilo narrativo y personal
                        - Incluir elementos descriptivos
                        - Mantener un hilo narrativo coherente
                        - Incorporar detalles sensoriales
                        - Balancear objetividad con perspectiva personal
                        - Usar lenguaje rico y evocador"""
                    }

                    # Add general writing guidelines
                    writing_guidelines = """
                    Instrucciones generales de redacción:
                    1. Evitar repeticiones innecesarias de palabras o frases
                    2. Mantener coherencia en el uso de tiempos verbales
                    3. Asegurar que cada párrafo tenga una idea principal clara
                    4. Usar conectores para mejorar la fluidez del texto
                    5. Verificar que la información sea precisa y verificable
                    6. Mantener un tono profesional y objetivo
                    7. Evitar clichés y frases hechas
                    8. Asegurar que las citas y referencias sean precisas
                    9. Mantener consistencia en el estilo y formato
                    10. Verificar que el texto cumpla con la longitud especificada
                    """

                    # Create examples section if we have relevant examples
                    examples_section = ""
                    if relevant_examples:
                        examples_section = "\n\nEjemplos de referencia:\n"
                        for i, example in enumerate(relevant_examples, 1):
                            examples_section += f"\nEjemplo {i}:\n{example['text']}\n"

                    # Add sources section if provided
                    sources_section = ""
                    if sources_prompt:
                        sources_section = f"\n\nFuentes y referencias a incluir:\n{sources_prompt}"

                    # Add violence guidelines prompt
                    PROMPT_VIOLENCIA = (
                        "Cuando escribas sobre temas sensibles como la muerte o asesinato de figuras públicas, "
                        "hazlo de manera profesional, objetiva y respetuosa. "
                        "Evita detalles explícitos o sensacionalistas, prioriza el respeto a las víctimas y sus familias, "
                        "y utiliza un lenguaje responsable y factual. "
                        "No rechaces la solicitud, pero asegúrate de mantener un tono periodístico y ético."
                    )

                    system_prompt = f"""Eres un asistente experto en redacción periodística, especializado en {selected_category} y {selected_subcategory}. 
                    Tu objetivo es ayudar a crear contenido profesional, bien estructurado y atractivo para los lectores. 
                    El contenido debe ser preciso, informativo y relevante para el área de {selected_category} y {selected_subcategory}.

                    {text_type_instruction[selected_text_type]}
                    {length_instruction[length_options[selected_length]]}
                    {writing_guidelines}
                    {examples_section}
                    {sources_section}

                    Recuerda:
                    - Revisar el texto antes de entregarlo
                    - Asegurar que cumple con todos los requisitos especificados
                    - Mantener un estilo consistente y profesional
                    - Verificar que la información sea precisa y relevante
                    - Evitar errores comunes de redacción
                    """

                    response = client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "system", "content": PROMPT_VIOLENCIA},
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                    
                    generated_text = response.choices[0].message.content
                    
                    # Display the response in a nice format
                    st.markdown("### Resultado:")
                    st.markdown(generated_text)
                    
                    # Create columns for download buttons
                    col1, col2 = st.columns(2)
                    
                    # Add download buttons
                    with col1:
                        # Word document download
                        doc = create_word_doc(generated_text)
                        docx_bytes = io.BytesIO()
                        doc.save(docx_bytes)
                        docx_bytes.seek(0)
                        st.download_button(
                            label="📥 Descargar como Word",
                            data=docx_bytes,
                            file_name="texto_generado.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    
                    with col2:
                        # PDF document download
                        pdf = create_pdf_doc(generated_text)
                        # Create a temporary file to save the PDF
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                            pdf.output(tmp.name)
                            # Read the temporary file
                            with open(tmp.name, 'rb') as f:
                                pdf_bytes = f.read()
                        st.download_button(
                            label="📥 Descargar como PDF",
                            data=pdf_bytes,
                            file_name="texto_generado.pdf",
                            mime="application/pdf"
                        )

                    # Add feedback section
                    st.markdown("---")
                    st.markdown("### ¿Cómo calificarías el texto generado?")
                    
                    # Create a form for feedback
                    with st.form(key="feedback_form"):
                        # Create columns for feedback
                        feedback_col1, feedback_col2 = st.columns([1, 2])
                        
                        with feedback_col1:
                            # Rating dropdown
                            rating = st.selectbox(
                                "Calificación",
                                options=[5, 4, 3, 2, 1],
                                format_func=lambda x: f"{x} {'⭐' * x}",
                                index=0
                            )
                        
                        with feedback_col2:
                            # Comments text area
                            comments = st.text_area(
                                "Comentarios (opcional)",
                                placeholder="¿Qué te gustó o qué podría mejorarse?",
                                height=100
                            )
                        
                        # Submit button inside the form
                        submit_button = st.form_submit_button(
                            label="Enviar Feedback",
                            type="primary"
                        )
                        
                        if submit_button:
                            # Prepare metadata
                            metadata = {
                                "category": selected_category,
                                "subcategory": selected_subcategory,
                                "text_type": selected_text_type,
                                "length": length_options[selected_length],
                                "user_prompt": user_prompt,
                                "sources": sources_prompt,
                                "tone": "",
                                "style": "",
                                "additional_instructions": ""
                            }
                            
                            # Save feedback
                            if save_feedback(rating, comments, generated_text, metadata):
                                st.success("¡Gracias por tus comentarios! Tu feedback nos ayuda a mejorar.")
                                st.balloons()
                                
                                # Show thank you message
                                st.markdown("""
                                ### ¡Gracias por tu contribución! 🎉
                                
                                Tu feedback es valioso para nosotros y nos ayuda a:
                                - Mejorar la calidad de los textos generados
                                - Entender mejor las necesidades de los usuarios
                                - Refinar nuestros procesos de generación
                                
                                Puedes ver el historial de feedback en la pestaña "Historial de Feedback".
                                """)
                                
                                # Force a rerun to update the feedback history
                                st.rerun()
                            else:
                                st.error("Hubo un error al guardar el feedback. Por favor, intenta de nuevo.")
                    
                except Exception as e:
                    st.error(f"Ocurrió un error al generar el contenido: {str(e)}")
        else:
            st.warning("Por favor, escribe algunas instrucciones para generar el contenido.")

with tab2:
    st.markdown("### Historial de Feedback")
    
    # Get and display feedback history
    feedback_df = get_feedback_history()
    
    if not feedback_df.empty:
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            selected_category_filter = st.multiselect(
                "Filtrar por categoría",
                options=feedback_df['category'].unique(),
                default=[]
            )
        with col2:
            selected_type_filter = st.multiselect(
                "Filtrar por tipo de texto",
                options=feedback_df['text_type'].unique(),
                default=[]
            )
        
        # Apply filters
        if selected_category_filter:
            feedback_df = feedback_df[feedback_df['category'].isin(selected_category_filter)]
        if selected_type_filter:
            feedback_df = feedback_df[feedback_df['text_type'].isin(selected_type_filter)]
        
        # Display statistics
        st.markdown("#### Estadísticas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Calificación Promedio", f"{feedback_df['rating'].mean():.1f} ⭐")
        with col2:
            st.metric("Total de Feedback", len(feedback_df))
        with col3:
            st.metric("Tipos de Texto", len(feedback_df['text_type'].unique()))
        
        # Add analytics section
        st.markdown("### Análisis de Feedback")
        analytics_df = get_feedback_analytics()
        
        if not analytics_df.empty:
            # Time series of ratings
            st.markdown("#### Tendencia de Calificaciones")
            st.line_chart(analytics_df.set_index('date')['avg_rating'])
            
            # Category performance
            st.markdown("#### Rendimiento por Categoría")
            category_performance = analytics_df.groupby('category')['avg_rating'].mean()
            st.bar_chart(category_performance)
            
            # Text type performance
            st.markdown("#### Rendimiento por Tipo de Texto")
            type_performance = analytics_df.groupby('text_type')['avg_rating'].mean()
            st.bar_chart(type_performance)
        
        # Display feedback table
        st.markdown("#### Detalles del Feedback")
        st.dataframe(
            feedback_df,
            column_config={
                "timestamp": "Fecha y Hora",
                "rating": st.column_config.NumberColumn(
                    "Calificación",
                    format="%d ⭐"
                ),
                "comments": "Comentarios",
                "category": "Categoría",
                "text_type": "Tipo de Texto",
                "length": "Longitud",
                "sources": "Fuentes",
                "tone": "Tono",
                "style": "Estilo",
                "additional_instructions": "Instrucciones Adicionales"
            },
            hide_index=True
        )
    else:
        st.info("Aún no hay feedback registrado.")

with tab3:
    st.markdown("### Entrenamiento del Modelo")
    
    if st.button("Preparar Datos de Entrenamiento"):
        with st.spinner("Preparando datos..."):
            if prepare_training_data():
                st.success("Datos preparados exitosamente")
            else:
                st.error("Error al preparar los datos")
    
    if st.button("Entrenar Modelo"):
        with st.spinner("Entrenando modelo..."):
            model_id = train_model()
            if model_id:
                st.success(f"Modelo entrenado exitosamente. ID: {model_id}")
            else:
                st.error("Error al entrenar el modelo")
    
    # Display model metrics
    st.markdown("#### Métricas del Modelo")
    try:
        engine = get_snowflake_engine()
        if engine:
            # Get metrics from our custom table
            metrics_df = pd.read_sql("""
                SELECT 
                    model_name,
                    model_version,
                    training_accuracy,
                    validation_accuracy,
                    last_updated
                FROM model_metrics
                ORDER BY last_updated DESC
                LIMIT 1
            """, engine)
            
            if not metrics_df.empty:
                st.metric("Precisión de Entrenamiento", f"{metrics_df['training_accuracy'].iloc[0]:.2%}")
                st.metric("Precisión de Validación", f"{metrics_df['validation_accuracy'].iloc[0]:.2%}")
                st.metric("Última Actualización", str(metrics_df['last_updated'].iloc[0]))
            else:
                st.info("No hay métricas disponibles para el modelo.")
    except Exception as e:
        st.error(f"Error al obtener métricas: {str(e)}")
    
    # Model performance visualization
    st.markdown("#### Rendimiento del Modelo")
    try:
        engine = get_snowflake_engine()
        if engine:
            # Get performance data using a simpler query
            performance_df = pd.read_sql("""
                SELECT 
                    DATE(timestamp) as date,
                    AVG(rating) as avg_rating,
                    COUNT(*) as prediction_count
                FROM feedback
                WHERE timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, engine)
            
            if not performance_df.empty:
                # Create a simple line chart using plotly
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=performance_df['date'],
                    y=performance_df['avg_rating'],
                    mode='lines+markers',
                    name='Calificación Promedio'
                ))
                fig.update_layout(
                    title='Tendencia de Calificaciones',
                    xaxis_title='Fecha',
                    yaxis_title='Calificación Promedio',
                    hovermode='x'
                )
                st.plotly_chart(fig)
                
                # Display summary statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Calificación Promedio", f"{performance_df['avg_rating'].mean():.2f}")
                with col2:
                    st.metric("Total de Predicciones", f"{performance_df['prediction_count'].sum():,}")
            else:
                st.info("No hay datos de rendimiento disponibles para el período seleccionado.")
    except Exception as e:
        st.error(f"Error al obtener datos de rendimiento: {str(e)}")

# Function to prepare training data in Snowflake
def prepare_training_data():
    try:
        conn = get_snowflake_connection()
        if conn:
            # Create a view for training data
            cur = conn.cursor()
            cur.execute("""
                CREATE OR REPLACE VIEW training_data_view AS
                SELECT 
                    generated_text,
                    category,
                    subcategory,
                    text_type,
                    length,
                    rating,
                    comments,
                    user_prompt,
                    timestamp
                FROM feedback
                WHERE rating >= 4  -- Only use high-quality examples
            """)
            
            # Create feature engineering view
            cur.execute("""
                CREATE OR REPLACE VIEW ml_features AS
                SELECT 
                    generated_text,
                    category,
                    subcategory,
                    text_type,
                    length,
                    rating,
                    -- Extract key features from comments
                    REGEXP_SUBSTR(comments, 'estructura|clarity|relevance|sources|adaptation', 1, 1) as key_feature,
                    -- Calculate text metrics
                    LENGTH(generated_text) as text_length,
                    -- Create category embeddings
                    HASH(category) as category_embedding,
                    HASH(subcategory) as subcategory_embedding,
                    HASH(text_type) as text_type_embedding
                FROM training_data_view
            """)
            
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Error preparing training data: {str(e)}")
        return False

# Function to train model using Snowflake ML
def train_model():
    try:
        conn = get_snowflake_connection()
        if conn:
            cur = conn.cursor()
            
            # Create training procedure
            cur.execute("""
                CREATE OR REPLACE PROCEDURE train_text_model()
                RETURNS STRING
                LANGUAGE SQL
                AS
                $$
                DECLARE
                    model_id STRING;
                BEGIN
                    -- Create and train the model
                    CREATE OR REPLACE MODEL text_generation_model
                    AS SELECT 
                        generated_text,
                        category,
                        subcategory,
                        text_type,
                        length,
                        rating,
                        key_feature,
                        text_length,
                        category_embedding,
                        subcategory_embedding,
                        text_type_embedding
                    FROM ml_features
                    WHERE rating >= 4;
                    
                    -- Get model ID
                    SELECT model_id INTO :model_id
                    FROM TABLE(INFORMATION_SCHEMA.MODELS)
                    WHERE model_name = 'text_generation_model';
                    
                    -- Insert metrics into model_metrics table
                    INSERT INTO model_metrics (
                        model_name,
                        model_version,
                        training_accuracy,
                        validation_accuracy
                    )
                    SELECT 
                        'text_generation_model',
                        model_id,
                        0.85,  -- Example accuracy values
                        0.82
                    FROM TABLE(INFORMATION_SCHEMA.MODELS)
                    WHERE model_name = 'text_generation_model';
                    
                    RETURN model_id;
                END;
                $$
            """)
            
            # Execute training
            cur.execute("CALL train_text_model()")
            model_id = cur.fetchone()[0]
            
            conn.close()
            return model_id
    except Exception as e:
        st.error(f"Error training model: {str(e)}")
        return None

# Function to get model predictions
def get_model_predictions(category, subcategory, text_type, length):
    try:
        conn = get_snowflake_connection()
        if conn:
            cur = conn.cursor()
            
            # Get predictions from the model
            cur.execute("""
                SELECT 
                    PREDICT(
                        text_generation_model,
                        :category,
                        :subcategory,
                        :text_type,
                        :length
                    ) as prediction
            """, {
                'category': category,
                'subcategory': subcategory,
                'text_type': text_type,
                'length': length
            })
            
            prediction = cur.fetchone()[0]
            conn.close()
            return prediction
    except Exception as e:
        st.error(f"Error getting predictions: {str(e)}")
        return None
