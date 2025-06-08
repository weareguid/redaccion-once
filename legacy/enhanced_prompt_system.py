# Enhanced Prompt System for Once Noticias Content Generation
# Updated with comprehensive editorial style guidelines and user-controlled length

import openai
import requests
from datetime import datetime
import json

class OnceNoticiasPromptSystem:

    def __init__(self, openai_client):
        self.client = openai_client
        self.brand_voice = {
            "tone": "Profesional, objetivo y accesible",
            "style": "Directo pero elaborado, con rigor periodístico",
            "values": "Veracidad, transparencia, servicio público",
            "audience": "Audiencia general mexicana interesada en información de calidad",
            "institutional_approach": "Tono institucional propositivo cuando se cubren iniciativas gubernamentales, manteniendo objetividad",
            "neutrality": "Imparcialidad sin omitir datos contrarios si son relevantes"
        }

        # Opciones de longitud disponibles para el usuario
        self.length_options = {
            "Auto": "auto",
            "Corta (100-300 palabras)": "corta",
            "Media (301-500 palabras)": "media",
            "Larga (501-800 palabras)": "larga",
            "Muy larga (801+ palabras)": "muy_larga"
        }

        # Patrones específicos por tipo de contenido según investigación
        # NOTA: Se removieron restricciones de longitud fijas para permitir control del usuario
        self.content_type_patterns = {
            "Nota Periodística": {
                "structure": "Pirámide invertida estricta",
                "opening_pattern": "Hecho principal con contexto de quién, qué, cuándo, dónde en primera oración",
                "recommended_length": "Breve (1-2 párrafos principales, 1 minuto de lectura)",  # Solo para Auto
                "tone": "Objetivo, institucional, neutral, sin juicios del redactor",
                "language": "Formal y directo, evita lenguaje florido, cada palabra tiene función informativa",
                "closing": "Abrupto tras cubrir datos clave, sin conclusión editorial",
                "voice": "Tercera persona siempre",
                "sentence_structure": "Sujeto + verbo + complemento directo sin subordinadas excesivas"
            },
            "Artículo": {
                "structure": "Bloques temáticos con subtítulos, no pirámide invertida estricta",
                "opening_pattern": "Introducción contextual o interrogativa para enganchar",
                "recommended_length": "Extenso (2-4 minutos de lectura, desarrollo completo)",  # Solo para Auto
                "tone": "Explicativo con mayor desarrollo narrativo, objetivo pero pedagógico",
                "language": "Más elaborado pero accesible, permite recursos estilísticos moderados",
                "closing": "Conclusión que resume hallazgos o reflexión final respaldada",
                "voice": "Tercera persona, voz narrativa que guía al lector",
                "sentence_structure": "Oraciones más amplias con conectores para articular ideas"
            },
            "Guión de TV": {
                "structure": "Fragmentos cortos aptos para lectura en voz alta",
                "opening_pattern": "Presentación breve del tema por conductor, resaltando lo relevante",
                "recommended_length": "Muy conciso, pensado para tiempos de transmisión (30-90 segundos típico)",  # Solo para Auto
                "tone": "Directo, conversacional formal, ligeramente más cálido",
                "language": "Muy accesible, oraciones cortas en presente, evita tecnicismos complejos",
                "closing": "Conclusión breve o regreso al presentador",
                "voice": "Para ser hablado, incluye indicaciones técnicas",
                "sentence_structure": "Frases muy cortas, separadas para respiración oral"
            },
            "Crónica": {
                "structure": "Narrativa de historia: introducción vívida, desarrollo cronológico/temático, desenlace",
                "opening_pattern": "Escena fuerte que sitúa al lector en medio de la acción",
                "recommended_length": "Variable según profundidad narrativa, dosifica información a lo largo del relato",  # Solo para Auto
                "tone": "Narrativo e inmersivo, mezcla objetividad con estilo literario",
                "language": "Rico en detalles sensoriales y descriptivos, más literario sin perder claridad",
                "closing": "Golpe emocional o moraleja, última cita significativa",
                "voice": "Tercera persona narrativa, incluye observaciones del cronista",
                "sentence_structure": "Variada según ritmo narrativo, incluye diálogos integrados"
            }
        }

        # Patrones específicos por categoría temática (sin restricciones de longitud)
        self.category_patterns = {
            "Economía": {
                "tone_specifics": "Objetivo y técnicamente preciso, énfasis en datos cuantitativos",
                "language_style": "Técnico accesible, explica indicadores con claridad",
                "opening_patterns": ["La presidenta X celebró que...", "Banxico reportó...", "El PIB mostró..."],
                "data_emphasis": "Cifras exactas con comparaciones temporales",
                "sources": ["INEGI", "Banxico", "SHCP", "analistas económicos"],
                "closing_patterns": ["se espera que... en próximos meses", "último dato relevante"]
            },
            "Política": {
                "tone_specifics": "Institucional equilibrado y respetuoso, imparcialidad",
                "language_style": "Muy formal y cuidadoso, evita adjetivos descalificativos",
                "opening_patterns": ["El Senado aprobó...", "El Presidente anunció...", "La Secretaría informó..."],
                "data_emphasis": "Declaraciones oficiales y objetivos anunciados",
                "sources": ["funcionarios oficiales", "comunicados presidenciales", "actores políticos"],
                "closing_patterns": ["la propuesta será enviada a...", "última declaración oficial"]
            },
            "Justicia": {
                "tone_specifics": "Formal y técnico, casi telegráficamente oficial, sin sensacionalismo",
                "language_style": "Extremadamente institucional y preciso, términos jurídicos específicos",
                "opening_patterns": ["La Fiscalía X obtuvo...", "Elementos de la Guardia Nacional detuvieron..."],
                "data_emphasis": "Detalles exactos de procedimientos, evidencias enumeradas",
                "sources": ["FGR", "comunicados oficiales", "autoridades policiales"],
                "closing_patterns": ["quedaron a disposición del juez...", "situación jurídica resultante"]
            },
            "Sociedad": {
                "tone_specifics": "Combina objetividad informativa con tono humano y cercano",
                "language_style": "Claro, sencillo y positivo, lenguaje inclusivo",
                "opening_patterns": ["La SEP anunció...", "La Secretaría de Salud informó...", "Miles de personas..."],
                "data_emphasis": "Beneficiarios, impacto social, información práctica",
                "sources": ["secretarías sociales", "ONGs", "ciudadanos beneficiarios"],
                "closing_patterns": ["la dependencia invitó a...", "información práctica final"]
            },
            "Transporte": {
                "tone_specifics": "Factual y orientado al usuario, positivo/enfocado en mejoras",
                "language_style": "Muy claro y utilitario, cifras exactas de impacto práctico",
                "opening_patterns": ["Este sábado inicia...", "Mañana entra en operación..."],
                "data_emphasis": "Características operativas, rutas, horarios, tarifas",
                "sources": ["Secretaría de Movilidad", "Servicio de Transportes Eléctricos"],
                "closing_patterns": ["último dato operativo", "información de acceso"]
            },
            "Energía": {
                "tone_specifics": "Serio y técnico, enfatiza impacto nacional",
                "language_style": "Técnico con contexto para entender magnitud",
                "opening_patterns": ["La Secretaría de Energía inauguró...", "Se reportó un récord..."],
                "data_emphasis": "Capacidad en MW, inversión, ahorro estimado",
                "sources": ["Sener", "CFE", "Pemex", "empresas energéticas"],
                "closing_patterns": ["factual con futuro inmediato"]
            },
            "Comercio": {
                "tone_specifics": "Neutro propio de negocios, enfoque en acuerdos y cifras",
                "language_style": "Técnico comercial pero comprensible",
                "opening_patterns": ["México y X firmaron...", "Las exportaciones crecieron..."],
                "data_emphasis": "Cifras financieras, volumen comercial, rankings",
                "sources": ["Secretaría de Economía", "cancillería", "organismos comerciales"],
                "closing_patterns": ["siguiente expectativa comercial"]
            },
            "Internacional": {
                "tone_specifics": "Objetivo y descriptivo, contextualiza para audiencia mexicana",
                "language_style": "Formal estándar internacional, español neutro",
                "opening_patterns": ["En Francia...", "El presidente de X...", "Un terremoto..."],
                "data_emphasis": "Contexto para lector no especializado",
                "sources": ["líderes mundiales", "organismos internacionales", "agencias"],
                "closing_patterns": ["situación actual o próximo evento"]
            }
        }

        # Elementos recurrentes identificados
        self.recurring_elements = {
            "attribution_patterns": [
                "La Fiscalía General de la República informó que...",
                "El Servicio de Transportes Eléctricos informó que...",
                "Sheinbaum celebró que...",
                "La presidenta X destacó que...",
                "Según cifras del INEGI...",
                "De acuerdo con el reporte..."
            ],
            "contextual_integration": [
                "El senador de Morena, [nombre], quien encabeza [cargo], refrendó que...",
                "Durante la décimo segunda edición de...",
                "Por segunda ocasión en menos de un mes..."
            ],
            "mexican_context_indicators": [
                "México", "mexicano", "nacional", "país", "pesos", "gobierno federal",
                "INEGI", "Banxico", "presidente", "estados", "población mexicana",
                "nuestro país"
            ]
        }

    def get_length_instruction(self, selected_length, text_type):
        """
        Genera instrucciones de longitud basadas en la selección del usuario
        """
        if selected_length == "auto":
            # Usar recomendaciones específicas del tipo de contenido
            content_patterns = self.content_type_patterns.get(text_type, {})
            recommended = content_patterns.get("recommended_length", "")

            length_instruction = f"""
LONGITUD OBJETIVO (AUTOMÁTICA): {recommended}
- Esta longitud está optimizada para el tipo de contenido {text_type} según estándares Once Noticias
- Ajustar según sea necesario para cubrir completamente la información esencial
"""

            # Instrucciones específicas adicionales por tipo cuando es Auto
            if text_type == "Nota Periodística":
                length_instruction += "- PÁRRAFOS: 2-3 párrafos principales máximo\n- TIEMPO DE LECTURA: 1-2 minutos\n"
            elif text_type == "Artículo":
                length_instruction += "- SECCIONES: 3-8 bloques temáticos\n- TIEMPO DE LECTURA: 2-4 minutos\n"
            elif text_type == "Guión de TV":
                length_instruction += "- DURACIÓN: 30-90 segundos de lectura oral\n- BLOQUES: Segmentos breves para transmisión\n"
            elif text_type == "Crónica":
                length_instruction += "- DESARROLLO: Variable según narrativa, sin límite fijo\n- ESTRUCTURA: Completa desde escena inicial hasta reflexión final\n"

        else:
            # Usar la longitud especificada por el usuario
            length_mappings = {
                        "corta": "El texto debe ser conciso y directo, entre 100 y 300 palabras.",
                        "media": "El texto debe tener una extensión media, entre 301 y 500 palabras.",
                        "larga": "El texto debe ser detallado y extenso, entre 501 y 800 palabras.",
                        "muy_larga": "El texto debe ser muy detallado y extenso, con más de 801 palabras."
                    }

            target_length = length_mappings.get(selected_length, "media")
            length_instruction = f"""
LONGITUD OBJETIVO (ESPECIFICADA POR USUARIO): {target_length}
- Cumplir estrictamente con esta longitud sin importar el tipo de contenido
- Ajustar la profundidad del contenido según el espacio disponible
- Mantener todos los elementos esenciales dentro de este límite
"""

        return length_instruction

    def get_real_time_context(self, topic, category):
        """
        Simula búsqueda de contexto en tiempo real
        En implementación real, integraría APIs de noticias, datos económicos, etc.
        """
        context_data = {
            "recent_developments": [],
            "key_data": {},
            "related_news": [],
            "expert_sources": []
        }

        # Aquí integrarías APIs como:
        # - Google News API
        # - INEGI API
        # - Banco de México API
        # - Reuters/Bloomberg APIs

        return context_data

    def create_enhanced_system_prompt(self, category, subcategory, text_type, user_prompt, sources="", selected_length="auto"):
        """
        Crea un prompt sistemático específico para Once Noticias basado en la investigación editorial
        Ahora incluye control de longitud por parte del usuario
        """

        # Obtener patrones específicos
        content_patterns = self.content_type_patterns.get(text_type, {})
        category_patterns = self.category_patterns.get(category, {})

        # Generar instrucciones de longitud
        length_instruction = self.get_length_instruction(selected_length, text_type)

        base_prompt = f"""
IDENTIDAD EDITORIAL: Eres un periodista experto de Once Noticias, reconocido medio mexicano digital (versión de Canal Once) comprometido con el rigor periodístico y el servicio público.

ESPECIALIZACIÓN: Experto en {category} - {subcategory} con profundo conocimiento del contexto mexicano.

TIPO DE CONTENIDO: {text_type}

VOZ EDITORIAL ONCE NOTICIAS:
- Tono: {self.brand_voice['tone']}
- Estilo: {self.brand_voice['style']}
- Valores: {self.brand_voice['values']}
- Audiencia: {self.brand_voice['audience']}
- Enfoque: {self.brand_voice['institutional_approach']}
- Neutralidad: {self.brand_voice['neutrality']}

{length_instruction}

CARACTERÍSTICAS ESPECÍFICAS PARA {text_type.upper()}:
"""

        # Agregar patrones específicos del tipo de contenido (sin menciones de longitud fija)
        if content_patterns:
            base_prompt += f"""
- ESTRUCTURA: {content_patterns.get('structure', '')}
- PATRÓN DE APERTURA: {content_patterns.get('opening_pattern', '')}
- TONO ESPECÍFICO: {content_patterns.get('tone', '')}
- LENGUAJE: {content_patterns.get('language', '')}
- CIERRE: {content_patterns.get('closing', '')}
- VOZ NARRATIVA: {content_patterns.get('voice', '')}
- ESTRUCTURA ORACIONAL: {content_patterns.get('sentence_structure', '')}
"""

        # Agregar patrones específicos de la categoría
        if category_patterns:
            base_prompt += f"""

CARACTERÍSTICAS ESPECÍFICAS PARA {category.upper()}:
- TONO ESPECÍFICO: {category_patterns.get('tone_specifics', '')}
- ESTILO DE LENGUAJE: {category_patterns.get('language_style', '')}
- ÉNFASIS EN DATOS: {category_patterns.get('data_emphasis', '')}
- FUENTES TÍPICAS: {', '.join(category_patterns.get('sources', []))}
- PATRONES DE APERTURA COMUNES: {', '.join(category_patterns.get('opening_patterns', []))}
- PATRONES DE CIERRE: {', '.join(category_patterns.get('closing_patterns', []))}
"""

        # Estructura específica detallada por tipo (actualizada sin restricciones de longitud fijas)
        base_prompt += self._get_detailed_structure_guide(text_type, category, selected_length)

        # Criterios de calidad específicos
        base_prompt += f"""

CRITERIOS DE CALIDAD ONCE NOTICIAS:
1. PRECISIÓN FACTUAL: Información verificable con fuentes oficiales mexicanas
2. CLARIDAD COMUNICATIVA: Lenguaje accesible sin perder rigor periodístico
3. RELEVANCIA NACIONAL: Impacto directo en audiencia mexicana
4. EQUILIBRIO INFORMATIVO: Múltiples perspectivas cuando apropiado
5. CONTEXTO MEXICANO: Situar información en panorama nacional
6. SERVICIO PÚBLICO: Información útil para toma de decisiones ciudadanas
7. NEUTRALIDAD INSTITUCIONAL: Evitar juicios no atribuidos

ELEMENTOS RECURRENTES ONCE NOTICIAS:
- Usar verbos declarativos al inicio: "La Fiscalía informó...", "El Presidente anunció..."
- Integrar contexto en misma oración: cargos completos, fechas, lugares
- Atribución inmediata de fuentes: "según cifras del INEGI", "de acuerdo con..."
- Referencias a México: ocasionalmente "nuestro país" integrando al lector
- Precisión en términos técnicos con explicación breve cuando necesario

INSTRUCCIONES ESPECÍFICAS DE REDACCIÓN:
- Incluir título atractivo y preciso (20-80 caracteres)
- Usar datos actualizados y verificables con fuente
- Mantener tono profesional pero accesible
- Evitar jerga técnica sin explicación
- Incluir cifras específicas con comparaciones temporales
- Citas textuales breves entre comillas con atribución clara

FUENTES PROPORCIONADAS:
{sources if sources else "Sin fuentes específicas proporcionadas - usar fuentes oficiales típicas de la categoría"}

TAREA: {user_prompt}

FORMATO DE SALIDA: Generar contenido que emule exactamente el estilo editorial de Once Noticias según los patrones identificados, manteniendo la estructura, tono y características específicas del tipo de contenido y categoría solicitados, respetando estrictamente la longitud objetivo especificada.
"""

        return base_prompt

    def _get_detailed_structure_guide(self, text_type, category, selected_length):
        """Guías estructurales detalladas por tipo de contenido, adaptadas a longitud seleccionada"""

        # Base guides sin restricciones fijas de longitud
        guides = {
            "Nota Periodística": f"""

ESTRUCTURA DETALLADA NOTA PERIODÍSTICA - ONCE NOTICIAS:
1. LEAD (Primera oración): Responder QUÉ, QUIÉN, CUÁNDO, DÓNDE
   - Ejemplo patrón: "La presidenta Claudia Sheinbaum celebró que [hecho] [cifra], [contexto temporal], de acuerdo con [fuente oficial]"
   - Integrar atribución en misma línea

2. DESARROLLO: Información en orden de importancia
   - Cita textual breve de autoridad principal
   - Detalles específicos con datos exactos

3. CONTEXTO (Si espacio permite): Antecedentes necesarios muy concisos
   - Comparaciones temporales ("el nivel más bajo desde 2005")

4. CIERRE: Sin conclusión editorial, termina con último dato relevante
   - Puede incluir tuit oficial incrustado si relevante
""",

            "Artículo": f"""

ESTRUCTURA DETALLADA ARTÍCULO/REPORTAJE - ONCE NOTICIAS:
1. INTRODUCCIÓN: Contextualización o pregunta para enganchar
   - Puede plantear problemática o tema general

2. SECCIONES CON SUBTÍTULOS (ajustar cantidad según longitud):
   - Formato pregunta: "¿Cómo actúan los gigantes de internet?"
   - O descriptivos: "Antecedentes del proyecto"

3. DESARROLLO POR BLOQUES:
   - Cada sección profundiza un aspecto específico
   - Múltiples fuentes integradas (expertos, estudios, informes)

4. CONCLUSIÓN: Resume hallazgos o deja reflexión final
   - Basada en datos o cita de especialista
""",

            "Guión de TV": f"""

ESTRUCTURA DETALLADA GUIÓN TV - ONCE NOTICIAS:
1. CABEZA: Presentación tema
   - "Buenas tardes. [Titular breve resaltando relevante]"

2. DESARROLLO: Información principal con indicaciones técnicas
   - (VIDEO: imágenes del evento) mientras narración
   - (GRÁFICO: estadística) al mencionar cifras

3. TOTALES/SOUNDBITES: Declaraciones fuentes
   - (SOT Funcionario: "...cita breve...")

4. CIERRE: Conclusión y regreso
   - "Con información de X, regresamos al estudio"

LENGUAJE: Oraciones muy cortas, presente/pretérito simple
INDICACIONES: Incluir (VIDEO), (AUDIO), (GRÁFICO) según corresponda
""",

            "Crónica": f"""

ESTRUCTURA DETALLADA CRÓNICA - ONCE NOTICIAS:
1. ESCENA INICIAL: Descripción ambiental vívida
   - Detalles sensoriales: sonidos, olores, atmósfera
   - Situar al lector inmediatamente en la acción

2. NARRATIVA CRONOLÓGICA: Desarrollo con elementos descriptivos
   - Presentar personajes con nombres (humanizar)
   - Citas extensas integradas como diálogos

3. CONTEXTO INTEGRADO: Información de fondo natural
   - No cortar narrativa, sino integrar datos en la historia

4. CLÍMAX: Momento cumbre de la historia

5. REFLEXIÓN FINAL: Significado más amplio
   - Imagen final potente o frase concluyente de personaje

TONO: Narrativo inmersivo, tercera persona con observaciones del cronista
RECURSOS: Metáforas, descripciones, diálogos directos
"""
        }

        base_guide = guides.get(text_type, "")

        # Agregar nota específica sobre longitud si no es Auto
        if selected_length != "auto":
            length_note = f"""

NOTA IMPORTANTE SOBRE LONGITUD:
- Ajustar la profundidad de cada sección según el límite de palabras especificado
- Priorizar elementos más importantes si el espacio es limitado
- Mantener estructura característica del tipo de contenido dentro del límite establecido
"""
            base_guide += length_note

        return base_guide

    def create_category_specific_enhancement(self, category, subcategory):
        """Crea instrucciones específicas adicionales por categoría (sin restricciones de longitud)"""

        specific_instructions = {
            "Economía": """
INSTRUCCIONES ESPECÍFICAS ECONOMÍA:
- Iniciar con cifra o dato más importante
- Incluir comparaciones temporales obligatorias ("X% más que el año anterior")
- Citar fuentes oficiales: INEGI, Banxico, SHCP en primera referencia
- Usar términos técnicos precisos pero explicar implicaciones
- Ejemplo de frase tipo: "lo que significa una apreciación de 2.10% respecto al cierre anterior"
- Evitar adjetivos emocionales ("alarmante caída" → "la bolsa cayó X%, su nivel más bajo en N años")
""",

            "Política": """
INSTRUCCIONES ESPECÍFICAS POLÍTICA:
- Mencionar cargo completo en primera referencia: "La Jefa de Gobierno, Martí Batres, señaló..."
- Equilibrar con múltiples voces si relevante: "por su parte, la oposición..."
- Evitar calificativos descalificativos: usar "criticó" en lugar de "fulminó"
- Citar declaraciones textuales de mañaneras cuando aplique
- Mantener tono institucional respetuoso
""",

            "Justicia": """
INSTRUCCIONES ESPECÍFICAS JUSTICIA:
- Usar terminología jurídica exacta: "vinculación a proceso", "sentencia condenatoria"
- Enumerar evidencias con precisión: "16 armas largas, 73 cargadores, 1,509 cartuchos"
- Iniciar siempre con la acción de autoridad: "La FGR obtuvo..."
- Incluir situación jurídica final: "quedaron a disposición del juez"
- Evitar detalles escabrosos, mantener sobriedad
""",

            "Sociedad": """
INSTRUCCIONES ESPECÍFICAS SOCIEDAD:
- Usar lenguaje inclusivo: "las y los ciudadanos", "personas con discapacidad"
- Enfatizar beneficiarios y impacto social: "beneficiando a X personas"
- Incluir información práctica cuando sea programa: requisitos, ubicaciones
- Citar objetivos institucionales: "reafirmamos nuestro compromiso con..."
- Terminar con información de acceso si aplica
""",

            "Transporte": """
INSTRUCCIONES ESPECÍFICAS TRANSPORTE:
- Datos operativos precisos: rutas, horarios, tarifas, número de unidades
- Impacto cuantificado: "transportará a 36 mil personas diariamente"
- Conexiones con otros sistemas de transporte
- Información práctica para usuarios
- Beneficios específicos: gratuidad para ciertos grupos
""",

            "Internacional": """
INSTRUCCIONES ESPECÍFICAS INTERNACIONAL:
- Contextualizar para audiencia mexicana no especializada
- Explicar siglas internacionales primera vez: "OTAN, la alianza militar occidental"
- Usar nombres oficiales correctos y cargos apropiados
- Proporcionar antecedentes históricos breves si necesario
- Mantener neutralidad, citar "ambas partes" en conflictos
"""
        }

        return specific_instructions.get(category, "")

    def create_fact_checking_prompt(self, generated_content, category):
        """Prompt específico para verificación de hechos estilo Once Noticias"""

        return f"""
Actúa como editor senior de Once Noticias especializado en verificación de hechos.

CONTENIDO A REVISAR:
{generated_content}

VERIFICAR SEGÚN ESTÁNDARES ONCE NOTICIAS:

1. PRECISIÓN FACTUAL:
   - ¿Todas las cifras tienen fuente atribuida?
   - ¿Los cargos y nombres están correctos?
   - ¿Las fechas y datos temporales son coherentes?

2. ESTILO EDITORIAL ONCE NOTICIAS:
   - ¿Refleja el tono objetivo e institucional?
   - ¿Usa los patrones de atribución correctos ("informó que...", "según...")?
   - ¿Mantiene estructura apropiada para el tipo de contenido?

3. CONTEXTO MEXICANO:
   - ¿Incluye referencias apropiadas al contexto nacional?
   - ¿Usa fuentes oficiales mexicanas cuando corresponde?

4. CALIDAD LINGÜÍSTICA:
   - ¿Evita jerga sin explicación?
   - ¿Mantiene claridad sin perder rigor?

CATEGORÍA ESPECÍFICA ({category}):
{self.create_category_specific_enhancement(category, "")}

REPORTE DE VERIFICACIÓN:
- Calificación general (1-10)
- Elementos que requieren verificación adicional
- Aspectos que no siguen el estilo Once Noticias
- Recomendaciones específicas de mejora
- Fuentes adicionales sugeridas para confirmar información
"""

    def create_improvement_prompt(self, initial_content, quality_evaluation, category, text_type):
        """Crea prompt para mejorar contenido basado en evaluación de calidad"""

        issues = []
        for criterion, data in quality_evaluation.get("detailed_scores", {}).items():
            if data.get("score", 0) < 70:
                issues.extend(data.get("issues", []))

        recommendations = quality_evaluation.get("recommendations", [])

        return f"""
Como editor senior de Once Noticias, mejora el siguiente contenido que no cumple completamente los estándares editoriales:

CONTENIDO ORIGINAL:
{initial_content}

PROBLEMAS IDENTIFICADOS:
{chr(10).join(f"- {issue}" for issue in issues[:5])}

RECOMENDACIONES ESPECÍFICAS:
{chr(10).join(f"- {rec}" for rec in recommendations[:5])}

TIPO DE CONTENIDO: {text_type}
CATEGORÍA: {category}

INSTRUCCIONES DE MEJORA:
1. Mantener la información esencial del contenido original
2. Aplicar patrones de atribución típicos de Once Noticias
3. Mejorar estructura según el tipo de contenido
4. Fortalecer contexto mexicano y fuentes oficiales
5. Asegurar neutralidad institucional y tono apropiado

OBJETIVO: Generar una versión mejorada que cumpla con score ≥ 85/100 según estándares Once Noticias.
"""

    def generate_research_questions(self, topic, category):
        """Genera preguntas de investigación específicas para Once Noticias"""

        base_questions = [
            f"¿Cuál es el impacto específico de {topic} en la población mexicana?",
            f"¿Qué fuentes oficiales mexicanas han informado sobre {topic}?",
            f"¿Existen cifras recientes del INEGI, Banxico u otras instituciones sobre {topic}?",
            f"¿Qué declaraciones oficiales recientes existen sobre {topic}?",
            f"¿Cómo se compara {topic} con períodos anteriores en México?"
        ]

        category_specific = {
            "Economía": [
                "¿Cómo afecta esto a la inflación y poder adquisitivo mexicano?",
                "¿Qué sectores económicos mexicanos se ven más impactados?",
                "¿Cuáles son las proyecciones oficiales de crecimiento?",
                "¿Qué dice Banxico al respecto?",
                "¿Hay comparación con otros países de la región?"
            ],
            "Política": [
                "¿Qué posición tienen los diferentes partidos mexicanos?",
                "¿Cómo afecta esto a la gobernabilidad nacional?",
                "¿Qué declaraciones hay de Palacio Nacional?",
                "¿Hay reacciones del Congreso de la Unión?",
                "¿Qué impacto tiene en las próximas elecciones?"
            ],
            "Justicia": [
                "¿Qué informó la FGR oficialmente?",
                "¿Hay comunicados del Poder Judicial?",
                "¿Cuáles son los delitos específicos según el código penal?",
                "¿Qué precedentes legales existen en México?",
                "¿Hay estadísticas oficiales relacionadas?"
            ]
        }
        return base_questions + category_specific.get(category, [])

    def create_editorial_review_prompt(self, content, text_type, category):
        """Prompt para revisión editorial final estilo Once Noticias"""

        return f"""
Como editor senior de Once Noticias, evalúa este {text_type} de {category} considerando:

CONTENIDO:
{content}

CRITERIOS ESPECÍFICOS ONCE NOTICIAS:

1. IDENTIDAD EDITORIAL (30%):
   - ¿Refleja la voz institucional y objetiva de Once Noticias?
   - ¿Mantiene el equilibrio entre rigor y accesibilidad?
   - ¿Respeta los valores de veracidad y servicio público?

2. CALIDAD PERIODÍSTICA (25%):
   - ¿Cumple estándares de pirámide invertida (si es nota)?
   - ¿Usa correctamente los patrones de atribución?
   - ¿Incluye contexto mexicano apropiado?

3. AUDIENCIA OBJETIVO (20%):
   - ¿Es relevante para audiencia mexicana general?
   - ¿Explica términos técnicos apropiadamente?
   - ¿Proporciona información útil para ciudadanos?

4. COMPLETITUD INFORMATIVA (15%):
   - ¿Responde las 5W+H según corresponda?
   - ¿Incluye datos verificables con fuentes?
   - ¿Contextualiza apropiadamente la información?

5. ESTILO Y ESTRUCTURA (10%):
   - ¿Sigue la estructura específica del tipo de contenido?
   - ¿Usa el lenguaje apropiado para la categoría?
   - ¿Mantiene coherencia estilística?

EVALUACIÓN:
- Calificación por criterio (1-10)
- Calificación general ponderada
- 3 fortalezas principales identificadas
- 3 aspectos críticos a mejorar
- Recomendaciones específicas de edición
- ¿Está listo para publicación en Once Noticias? (Sí/No y por qué)
"""
