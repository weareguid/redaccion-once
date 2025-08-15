# Sistema de Generación de Supers para Once Noticias
# Genera texto sobreimpreso (supers) para notas televisivas

import re
from typing import Dict, List, Optional
from datetime import datetime
import json

class SuperGenerator:
    """Generador de supers televisivos siguiendo lineamientos de Canal Once"""
    
    def __init__(self):
        """Inicializa el generador de supers con las reglas de formato"""
        
        # Formatos base para cada tipo de super
        self.formats = {
            "CG_1L": "[CG :1L NOTICIAS 2025\\{content}]",
            "CG_2L": "[CG :2L NOTICIAS 2025\\{line1}\\{line2}]",
            "CG_3L": "[CG :3L NOTICIAS 2025\\{section}\\{location}\\{topic}]",
            "ALERTA_1L": "[CG :ALERTA ONCE 1L\\{content}]",
            "ALERTA_2L": "[CG :ALERTA ONCE 2L\\{line1}\\{line2}]",
            "CONDUCTOR": "[CG :CONDUCTOR 2025\\{name}\\{twitter}]",
            "FALLA_ORIGEN": "[CG :FALLA DE ORIGEN 2025\\{content}]",
            "SCROLL": "[CG :SCROLL\\{content}]"
        }
        
        # Límites de caracteres
        self.char_limits = {
            "CG_1L": 55,
            "CG_2L": 55,
            "CG_3L": 55,
            "ALERTA_1L": 55,
            "ALERTA_2L": 55,
            "CONDUCTOR": 50,
            "FALLA_ORIGEN": 15,
            "SCROLL": 633
        }
        
        # Instrucciones específicas por tipo
        self.type_instructions = {
            "CG_1L": """
                Genera un super de UNA LÍNEA que:
                - Capture la esencia de la noticia en máximo 55 caracteres
                - Sea claro, conciso y directo
                - Use verbos activos en presente o pasado reciente
                - Evite artículos innecesarios para ahorrar espacio
                - Priorice datos concretos sobre descripciones
                EJEMPLO: MTV INICIÓ TRANSMISIONES EN 1981
            """,
            
            "CG_2L": """
                Genera un super de DOS LÍNEAS donde:
                - Primera línea: idea principal o tema (máx 55 caracteres)
                - Segunda línea: contexto, dato adicional o consecuencia (máx 55 caracteres)
                - Ambas líneas deben complementarse sin repetir información
                - Mantener coherencia gramatical entre líneas
                EJEMPLO:
                Línea 1: MTV CAMBIÓ LA HISTORIA DE LA TV Y LA MÚSICA
                Línea 2: TRANSMITÍA MODA Y ESTÉTICA DE CELEBRIDADES
            """,
            
            "CG_3L": """
                Genera un super de TRES LÍNEAS para notas nacionales o internacionales:
                - Primera línea: NACIONAL o INTERNACIONAL (según corresponda)
                - Segunda línea: Estado/Ciudad o País (máx 55 caracteres)
                - Tercera línea: Tema o acontecimiento principal (máx 55 caracteres)
                EJEMPLO:
                Línea 1: NACIONAL
                Línea 2: ESTADO DE MÉXICO
                Línea 3: DESMANTELAN CENTRO DE MANDO CLANDESTINO
            """,
            
            "ALERTA_1L": """
                Genera un super de ALERTA de UNA LÍNEA para noticias de última hora:
                - Máximo 55 caracteres
                - Información urgente o breaking news
                - Tono de inmediatez
                - Datos confirmados únicamente
            """,
            
            "ALERTA_2L": """
                Genera un super de ALERTA de DOS LÍNEAS para noticias importantes:
                - Primera línea: hecho principal (máx 55 caracteres)
                - Segunda línea: detalles adicionales urgentes (máx 55 caracteres)
                - Mantener tono de alerta informativa
            """,
            
            "CONDUCTOR": """
                Genera identificación para conductor/a:
                - Primera línea: Nombre completo (máx 50 caracteres)
                - Segunda línea: Cuenta de X/Twitter con @ (máx 50 caracteres)
                EJEMPLO:
                Línea 1: NAHOMI RODRÍGUEZ
                Línea 2: @Nahomi_Rod11
            """,
            
            "FALLA_ORIGEN": """
                Genera indicador técnico breve:
                - Máximo 15 caracteres
                - Opciones típicas: VÍA ZOOM, VÍA TELEFÓNICA, AUDIO DE ORIGEN, VIDEO DE ORIGEN
                - Todo en mayúsculas
            """,
            
            "SCROLL": """
                Genera un cintillo informativo con múltiples noticias breves:
                - Máximo 633 caracteres en total
                - Separar cada noticia con asterisco (*)
                - Incluir 4-8 noticias breves
                - Priorizar información más relevante al inicio
                - Mantener estructura: HECHO + DATO CLAVE
                EJEMPLO: * SHEINBAUM LOGRA ACUERDO CON EUA * SEMAR VIGILA ARRIBO DE TORTUGAS * 91 PERSONAS ASESINADAS EN GAZA
            """
        }
    
    def validate_length(self, text: str, super_type: str, line_num: Optional[int] = None) -> bool:
        """
        Valida que el texto cumpla con los límites de caracteres
        
        Args:
            text: Texto a validar
            super_type: Tipo de super
            line_num: Número de línea (para supers multilínea)
            
        Returns:
            bool: True si cumple con el límite
        """
        limit = self.char_limits.get(super_type, 55)
        return len(text) <= limit
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """
        Trunca el texto respetando palabras completas
        
        Args:
            text: Texto a truncar
            max_length: Longitud máxima
            
        Returns:
            str: Texto truncado
        """
        if len(text) <= max_length:
            return text
        
        # Truncar y buscar último espacio
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            return truncated[:last_space]
        return truncated
    
    def format_super(self, super_type: str, content: Dict[str, str]) -> str:
        """
        Formatea el super según el tipo y contenido
        
        Args:
            super_type: Tipo de super
            content: Diccionario con el contenido por línea/sección
            
        Returns:
            str: Super formateado según especificaciones Canal Once
        """
        template = self.formats.get(super_type, "")
        
        if super_type == "CG_1L":
            return template.format(content=content.get("content", ""))
        
        elif super_type == "CG_2L":
            return template.format(
                line1=content.get("line1", ""),
                line2=content.get("line2", "")
            )
        
        elif super_type == "CG_3L":
            return template.format(
                section=content.get("section", "NACIONAL"),
                location=content.get("location", ""),
                topic=content.get("topic", "")
            )
        
        elif super_type == "ALERTA_1L":
            return template.format(content=content.get("content", ""))
        
        elif super_type == "ALERTA_2L":
            return template.format(
                line1=content.get("line1", ""),
                line2=content.get("line2", "")
            )
        
        elif super_type == "CONDUCTOR":
            return template.format(
                name=content.get("name", ""),
                twitter=content.get("twitter", "")
            )
        
        elif super_type == "FALLA_ORIGEN":
            return template.format(content=content.get("content", ""))
        
        elif super_type == "SCROLL":
            return template.format(content=content.get("content", ""))
        
        return ""
    
    def extract_key_info(self, news_content: str, category: str) -> Dict[str, str]:
        """
        Extrae información clave del contenido para generar supers
        
        Args:
            news_content: Contenido de la noticia
            category: Categoría de la noticia
            
        Returns:
            Dict con información clave extraída
        """
        key_info = {
            "main_topic": "",
            "location": "",
            "who": "",
            "what": "",
            "when": "",
            "data": [],
            "category": category
        }
        
        # Extraer primeras oraciones que suelen contener info clave
        sentences = news_content.split('.')[:5]
        
        # Buscar patrones comunes
        for sentence in sentences:
            # Buscar ubicaciones (estados, ciudades, países)
            location_patterns = [
                r"en (\w+(?:\s+\w+)*)",
                r"En (\w+(?:\s+\w+)*)",
                r"desde (\w+(?:\s+\w+)*)"
            ]
            for pattern in location_patterns:
                match = re.search(pattern, sentence)
                if match and not key_info["location"]:
                    key_info["location"] = match.group(1)
            
            # Buscar nombres de personas/instituciones
            if any(word in sentence for word in ["presidente", "secretario", "ministro", "director"]):
                key_info["who"] = sentence.strip()
            
            # Buscar datos numéricos
            numbers = re.findall(r'\d+(?:\.\d+)?(?:\s*(?:mil|millones|por ciento|%))?', sentence)
            if numbers:
                key_info["data"].extend(numbers)
        
        # Tema principal (primera oración limpia)
        if sentences:
            key_info["main_topic"] = sentences[0].strip()
        
        return key_info
    
    def create_prompts_for_super_type(self, super_type: str, news_content: str, 
                                     category: str, key_info: Dict) -> List[str]:
        """
        Crea prompts específicos para generar supers según el tipo
        
        Args:
            super_type: Tipo de super a generar
            news_content: Contenido completo de la noticia
            category: Categoría de la noticia
            key_info: Información clave extraída
            
        Returns:
            Lista de prompts para generar variaciones
        """
        base_instruction = self.type_instructions.get(super_type, "")
        
        # Contexto común
        context = f"""
        NOTICIA: {news_content[:500]}...
        CATEGORÍA: {category}
        INFORMACIÓN CLAVE:
        - Tema principal: {key_info.get('main_topic', '')}
        - Ubicación: {key_info.get('location', 'México')}
        - Datos relevantes: {', '.join(key_info.get('data', [])[:3])}
        """
        
        prompts = []
        
        # Generar 3 variaciones con diferentes enfoques
        if super_type in ["CG_1L", "ALERTA_1L"]:
            prompts = [
                f"{base_instruction}\n{context}\nGenera un super enfocado en el HECHO PRINCIPAL:",
                f"{base_instruction}\n{context}\nGenera un super enfocado en el DATO MÁS IMPACTANTE:",
                f"{base_instruction}\n{context}\nGenera un super enfocado en la CONSECUENCIA o IMPACTO:"
            ]
        
        elif super_type in ["CG_2L", "ALERTA_2L"]:
            prompts = [
                f"{base_instruction}\n{context}\nGenera un super con TEMA + CONTEXTO:",
                f"{base_instruction}\n{context}\nGenera un super con HECHO + DATO CLAVE:",
                f"{base_instruction}\n{context}\nGenera un super con ACCIÓN + RESULTADO:"
            ]
        
        elif super_type == "CG_3L":
            # Determinar si es nacional o internacional
            section = "INTERNACIONAL" if category == "Internacional" else "NACIONAL"
            prompts = [
                f"{base_instruction}\n{context}\nGenera un super de 3 líneas con sección={section}:"
            ]
        
        elif super_type == "SCROLL":
            prompts = [
                f"{base_instruction}\n{context}\nGenera un scroll resumiendo los puntos más importantes de la noticia:"
            ]
        
        else:
            # Para otros tipos, usar instrucción base
            prompts = [f"{base_instruction}\n{context}\nGenera el super:"]
        
        return prompts
    
    def parse_super_response(self, response: str, super_type: str) -> Dict[str, str]:
        """
        Parsea la respuesta del modelo para extraer las líneas del super
        
        Args:
            response: Respuesta del modelo
            super_type: Tipo de super
            
        Returns:
            Dict con el contenido parseado por líneas
        """
        content = {}
        
        # Limpiar respuesta
        response = response.strip()
        
        if super_type in ["CG_1L", "ALERTA_1L", "FALLA_ORIGEN", "SCROLL"]:
            # Super de una sola línea/contenido
            content["content"] = response.replace("\\n", " ").strip()
            
        elif super_type in ["CG_2L", "ALERTA_2L", "CONDUCTOR"]:
            # Super de dos líneas
            lines = response.split("\\n")
            if len(lines) >= 2:
                content["line1"] = lines[0].strip()
                content["line2"] = lines[1].strip()
            else:
                # Si viene en otro formato, intentar split por línea nueva
                lines = response.split("\n")
                if len(lines) >= 2:
                    content["line1"] = lines[0].strip()
                    content["line2"] = lines[1].strip()
                else:
                    content["line1"] = response.strip()
                    content["line2"] = ""
        
        elif super_type == "CG_3L":
            # Super de tres líneas
            lines = response.split("\\n")
            if len(lines) < 3:
                lines = response.split("\n")
            
            if len(lines) >= 3:
                content["section"] = lines[0].strip()
                content["location"] = lines[1].strip()
                content["topic"] = lines[2].strip()
            else:
                content["section"] = "NACIONAL"
                content["location"] = ""
                content["topic"] = response.strip()
        
        # Validar y truncar si es necesario
        for key, value in content.items():
            if key in ["line1", "line2", "content", "location", "topic", "name", "twitter"]:
                limit = self.char_limits.get(super_type, 55)
                if super_type == "SCROLL":
                    limit = 633
                content[key] = self.truncate_text(value, limit)
        
        return content
    
    def generate_super_proposals(self, super_type: str, news_content: str, 
                                category: str, num_proposals: int = 3) -> List[Dict]:
        """
        Genera múltiples propuestas de supers
        
        Args:
            super_type: Tipo de super a generar
            news_content: Contenido de la noticia
            category: Categoría de la noticia
            num_proposals: Número de propuestas a generar
            
        Returns:
            Lista de propuestas con formato y validación
        """
        proposals = []
        
        # Extraer información clave
        key_info = self.extract_key_info(news_content, category)
        
        # Crear prompts para diferentes enfoques
        prompts = self.create_prompts_for_super_type(super_type, news_content, category, key_info)
        
        # Por ahora, retornar propuestas de ejemplo basadas en la info extraída
        # En la integración real, estos se generarán con OpenAI
        
        for i in range(min(num_proposals, len(prompts))):
            proposal = {
                "type": super_type,
                "prompt_used": prompts[i] if i < len(prompts) else prompts[0],
                "content": {},
                "formatted": "",
                "valid": True,
                "char_count": {}
            }
            
            # Generar contenido de ejemplo basado en key_info
            if super_type == "CG_1L":
                main_topic = key_info.get("main_topic", "")[:50]
                proposal["content"] = {"content": main_topic.upper()}
                
            elif super_type == "CG_2L":
                main_topic = key_info.get("main_topic", "")[:50]
                location = key_info.get("location", "México")
                proposal["content"] = {
                    "line1": main_topic.upper()[:55],
                    "line2": f"EN {location.upper()}"[:55]
                }
                
            elif super_type == "CG_3L":
                section = "INTERNACIONAL" if category == "Internacional" else "NACIONAL"
                location = key_info.get("location", "MÉXICO").upper()
                topic = key_info.get("main_topic", "")[:50].upper()
                proposal["content"] = {
                    "section": section,
                    "location": location,
                    "topic": topic
                }
            
            elif super_type == "SCROLL":
                # Crear scroll con puntos clave
                points = []
                if key_info.get("main_topic"):
                    points.append(key_info["main_topic"][:100].upper())
                if key_info.get("data"):
                    for data in key_info["data"][:2]:
                        points.append(f"REPORTAN {data}".upper())
                scroll_content = " * ".join(points)[:633]
                proposal["content"] = {"content": scroll_content}
            
            else:
                # Otros tipos
                proposal["content"] = {"content": key_info.get("main_topic", "")[:50].upper()}
            
            # Formatear y validar
            proposal["formatted"] = self.format_super(super_type, proposal["content"])
            
            # Contar caracteres
            for key, value in proposal["content"].items():
                proposal["char_count"][key] = len(value)
            
            # Validar longitudes
            proposal["valid"] = all(
                len(v) <= self.char_limits.get(super_type, 55)
                for v in proposal["content"].values()
            )
            
            proposals.append(proposal)
        
        return proposals