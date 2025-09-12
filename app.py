import streamlit as st
import openai
from openai import OpenAI
import os
import json
import time
import pandas as pd
import sqlite3
from datetime import datetime
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

# Initialize OpenAI with error handling
def get_openai_client():
    try:
        # Try to get API key from secrets first, then environment variables
        api_key = None
        try:
            api_key = st.secrets["OPENAI"]["api_key"]
        except:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key == "sk-placeholder-key-replace-with-real-key":
            st.error("⚠️ OpenAI API key not configured. Please add your API key in the secrets or environment variables.")
            st.info("For local development, update the secrets.toml file. For Streamlit Cloud, add OPENAI_API_KEY in the secrets section.")
            return None
            
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error initializing OpenAI: {str(e)}")
        return None

# Initialize SQLite database for local storage
def init_sqlite_db():
    conn = sqlite3.connect('feedback.db')
    cur = conn.cursor()
    
    # Create feedback table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rating INTEGER,
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
    
    conn.commit()
    conn.close()

# Initialize database
init_sqlite_db()

# Function to save feedback to SQLite
def save_feedback(rating, comments, generated_text, metadata):
    try:
        conn = sqlite3.connect('feedback.db')
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO feedback (rating, comments, generated_text, category, text_type, length, sources, tone, style, additional_instructions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(rating),
            str(comments),
            str(generated_text),
            str(metadata['category']),
            str(metadata['text_type']),
            str(metadata['length']),
            str(metadata['sources']),
            str(metadata['tone']),
            str(metadata['style']),
            str(metadata['additional_instructions'])
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving feedback: {str(e)}")
        return False

# Function to get feedback history from SQLite
def get_feedback_history():
    try:
        conn = sqlite3.connect('feedback.db')
        df = pd.read_sql_query("""
            SELECT 
                timestamp,
                rating,
                comments,
                generated_text,
                category,
                text_type,
                length,
                sources,
                tone,
                style,
                additional_instructions
            FROM feedback
            ORDER BY timestamp DESC
        """, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error getting feedback history: {str(e)}")
        return pd.DataFrame()

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
    try:
        with open('training_data.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if 'metadata' in data and data['metadata']:
                        training_data.append(data)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        st.warning("Training data file not found. Using default examples.")
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
    "Internacional",
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
tab1, tab2 = st.tabs(["Generar Texto", "Historial de Feedback"])

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
        placeholder="Ingresa las fuentes, referencias o datos específicos que deseas incluir en el texto..."
    )
    st.caption("Nota: Las fuentes proporcionadas son solo para investigación y referencia. Nunca deben ser copiadas directamente en el contenido generado.")

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
            st.session_state.user_input = ""
            st.session_state.feedback_submitted = False
            # Rerun the app
            st.rerun()

    if generate_button:
        if user_prompt:
            # Get OpenAI client
            client = get_openai_client()
            if client is None:
                st.stop()
                
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

SIEMPRE incluye un título al inicio de cada nota, artículo, crónica, etc., a menos que el usuario especifique lo contrario.

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

# Add a sidebar with app info
with st.sidebar:
    st.markdown("## 📊 Información de la App")
    st.markdown("""
    **Asistente de Redacción Periodística**
    
    Esta aplicación te ayuda a generar contenido periodístico de alta calidad usando IA.
    
    **Características:**
    - Generación de contenido personalizado
    - Múltiples formatos de texto
    - Descarga en Word y PDF
    - Sistema de feedback
    - Historial de generaciones
    """)
    
    st.markdown("---")
    st.markdown("### 🔧 Configuración")
    
    # Check if API key is configured
    try:
        api_key = st.secrets["OPENAI"]["api_key"]
        if api_key and api_key != "sk-placeholder-key-replace-with-real-key":
            st.success("✅ OpenAI API configurada")
        else:
            st.warning("⚠️ OpenAI API no configurada")
    except:
        st.warning("⚠️ OpenAI API no configurada")
    
    st.markdown("---")
    st.markdown("### 📝 Instrucciones")
    st.markdown("""
    1. Selecciona la categoría y tipo de texto
    2. Escribe tus instrucciones
    3. Haz clic en "Generar"
    4. Descarga el resultado
    5. Proporciona feedback para mejorar
    """)
