# Quality Assurance System for Once Noticias
# Updated with comprehensive editorial standards

import re
import json
from typing import Dict, List, Tuple
from datetime import datetime
import pandas as pd

class OnceNoticiasQualityAssurance:

    def __init__(self):
        # Estándares editoriales específicos de Once Noticias basados en investigación
        self.editorial_standards = {
            "precision_factual": {
                "weight": 30,
                "criteria": [
                    "atribucion_fuentes_oficiales",
                    "datos_verificables",
                    "coherencia_temporal",
                    "fuentes_mexicanas_apropiadas"
                ]
            },
            "calidad_periodistica": {
                "weight": 25,
                "criteria": [
                    "estructura_tipo_contenido",
                    "patrones_atribucion",
                    "contexto_mexicano",
                    "lenguaje_institucional"
                ]
            },
            "relevancia_audiencia": {
                "weight": 20,
                "criteria": [
                    "impacto_poblacion_mexicana",
                    "accesibilidad_lenguaje",
                    "informacion_util_ciudadanos"
                ]
            },
            "completitud_informativa": {
                "weight": 15,
                "criteria": [
                    "cinco_w_mas_h",
                    "contexto_apropiado",
                    "datos_comparativos_temporales"
                ]
            },
            "identidad_editorial": {
                "weight": 10,
                "criteria": [
                    "voz_once_noticias",
                    "neutralidad_institucional",
                    "servicio_publico"
                ]
            }
        }

        # Métricas específicas por tipo de contenido Once Noticias
        self.content_type_metrics = {
            "Nota Periodística": {
                "lead_quality": {
                    "debe_incluir": ["qué", "quién", "cuándo", "dónde"],
                    "patron_apertura": "atribucion_autoridad_con_hecho",
                    "estructura": "piramide_invertida_estricta"
                },
                "length_standards": {
                    "tiempo_lectura": "1-2 minutos máximo",
                    "parrafos": {"min": 2, "max": 4}
                },
                "cierre": "sin_conclusion_editorial"
            },
            "Artículo": {
                "estructura_required": {
                    "introduccion": "contextual_o_interrogativa",
                    "subtitulos": "bloques_tematicos",
                    "desarrollo": "multiples_fuentes"
                },
                "length_standards": {
                    "tiempo_lectura": "2-4 minutos",
                    "secciones": {"min": 3, "max": 8}
                },
                "cierre": "conclusion_respaldada_datos"
            },
            "Guión de TV": {
                "formato_oral": {
                    "oraciones": "muy_cortas",
                    "tiempo_presente": "preferente",
                    "indicaciones_tecnicas": "requeridas"
                },
                "duracion": "segmentos_breves_transmision",
                "cierre": "regreso_presentador"
            },
            "Crónica": {
                "narrativa": {
                    "apertura": "escena_vivida_inmersiva",
                    "desarrollo": "cronologico_con_personajes",
                    "contexto": "integrado_naturalmente"
                },
                "recursos": "descripcion_sensorial_dialogos",
                "cierre": "reflexion_significado_amplio"
            }
        }

        # Patrones específicos por categoría Once Noticias
        self.category_patterns = {
            "Economía": {
                "datos_requeridos": ["cifras_especificas", "comparaciones_temporales", "fuentes_oficiales"],
                "fuentes_esperadas": ["INEGI", "Banxico", "SHCP"],
                "lenguaje": "tecnico_accesible",
                "enfoque": "impacto_poder_adquisitivo"
            },
            "Política": {
                "equilibrio": "multiples_voces_cuando_apropiado",
                "fuentes_esperadas": ["funcionarios_oficiales", "comunicados_presidenciales"],
                "lenguaje": "formal_institucional",
                "enfoque": "impacto_gobernabilidad"
            },
            "Justicia": {
                "terminologia": "juridica_precisa",
                "fuentes_esperadas": ["FGR", "autoridades_policiales"],
                "detalles": "procedimientos_evidencias",
                "enfoque": "situacion_juridica_final"
            },
            "Sociedad": {
                "lenguaje": "inclusivo_humano",
                "fuentes_esperadas": ["secretarias_sociales", "ciudadanos_beneficiarios"],
                "enfoque": "beneficio_social_acceso_programas",
                "informacion_practica": "requerida_cuando_aplique"
            },
            "Transporte": {
                "datos_operativos": ["rutas", "horarios", "tarifas", "capacidad"],
                "fuentes_esperadas": ["Secretaria_Movilidad", "STE"],
                "enfoque": "utilidad_practica_usuario",
                "impacto": "cuantificado_personas_beneficiadas"
            },
            "Internacional": {
                "contextualizacion": "audiencia_mexicana",
                "explicacion": "siglas_terminos_internacionales",
                "neutralidad": "ambas_partes_conflictos",
                "enfoque": "implicaciones_para_mexico"
            }
        }

        # Indicadores de contexto mexicano Once Noticias
        self.mexican_context_indicators = [
            "México", "mexicano", "nacional", "país", "pesos",
            "gobierno federal", "INEGI", "Banxico", "presidente",
            "estados", "población mexicana", "nuestro país"
        ]

        # Patrones de atribución Once Noticias
        self.attribution_patterns = [
            r"(?:La|El)\s+(?:Fiscalía|Secretaría|Presidente|Senado).*?(?:informó|anunció|señaló|celebró)\s+que",
            r"según\s+(?:cifras del|datos del|el reporte de)\s+(?:INEGI|Banxico|SHCP)",
            r"de acuerdo con\s+(?:el|la|los|las)\s+[A-Z][^.]{10,50}",
            r"[A-Z][^.]{5,30}\s+(?:destacó|confirmó|explicó|advirtió)\s+que"
        ]

    def evaluate_content_quality(self, content: str, metadata: Dict) -> Dict:
        """
        Evaluación completa según estándares específicos Once Noticias
        """
        text_type = metadata.get('text_type', '')
        category = metadata.get('category', '')

        evaluation = {
            "overall_score": 0,
            "detailed_scores": {},
            "once_noticias_compliance": {},
            "strengths": [],
            "critical_issues": [],
            "recommendations": [],
            "publication_ready": False,
            "timestamp": datetime.now().isoformat()
        }

        # Evaluación por criterios principales
        evaluation["detailed_scores"]["precision_factual"] = self.evaluate_factual_precision(content, category)
        evaluation["detailed_scores"]["calidad_periodistica"] = self.evaluate_journalistic_quality(content, text_type, category)
        evaluation["detailed_scores"]["relevancia_audiencia"] = self.evaluate_audience_relevance(content, category)
        evaluation["detailed_scores"]["completitud_informativa"] = self.evaluate_information_completeness(content, text_type)
        evaluation["detailed_scores"]["identidad_editorial"] = self.evaluate_editorial_identity(content)

        # Evaluación específica de cumplimiento Once Noticias
        evaluation["once_noticias_compliance"] = self.evaluate_once_noticias_compliance(content, text_type, category)

        # Cálculo score ponderado
        evaluation["overall_score"] = self.calculate_weighted_score(evaluation["detailed_scores"])

        # Determinar si está listo para publicación
        evaluation["publication_ready"] = self.determine_publication_readiness(evaluation)

        # Generar recomendaciones específicas
        evaluation["recommendations"] = self.generate_specific_recommendations(evaluation, text_type, category)

        return evaluation

    def evaluate_factual_precision(self, content: str, category: str) -> Dict:
        """Evalúa precisión factual según estándares Once Noticias"""
        score = 0
        issues = []
        strengths = []

        # Verificar presencia de fuentes oficiales mexicanas
        official_sources = ["INEGI", "Banxico", "SHCP", "FGR", "Secretaría", "Presidencia"]
        sources_found = sum(1 for source in official_sources if source in content)

        if sources_found >= 2:
            score += 40
            strengths.append("Incluye múltiples fuentes oficiales mexicanas")
        elif sources_found >= 1:
            score += 25
            strengths.append("Incluye fuente oficial mexicana")
        else:
            issues.append("Falta atribución a fuentes oficiales mexicanas")

        # Verificar patrones de atribución típicos Once Noticias
        attribution_count = 0
        for pattern in self.attribution_patterns:
            attribution_count += len(re.findall(pattern, content, re.IGNORECASE))

        if attribution_count >= 2:
            score += 35
            strengths.append("Usa patrones de atribución típicos de Once Noticias")
        elif attribution_count >= 1:
            score += 20
        else:
            issues.append("No usa patrones de atribución característicos de Once Noticias")

        # Verificar datos específicos con comparaciones temporales
        temporal_comparisons = re.findall(
            r'(?:desde|más que|menos que|nivel más alto|nivel más bajo)\s+(?:20\d{2}|el año|enero|febrero)',
            content, re.IGNORECASE
        )

        if temporal_comparisons:
            score += 25
            strengths.append("Incluye comparaciones temporales específicas")
        else:
            issues.append("Falta contexto temporal comparativo")

        return {
            "score": min(score, 100),
            "issues": issues,
            "strengths": strengths,
            "details": f"Fuentes oficiales: {sources_found}, Atribuciones: {attribution_count}"
        }

    def evaluate_journalistic_quality(self, content: str, text_type: str, category: str) -> Dict:
        """Evalúa calidad periodística específica Once Noticias"""
        score = 0
        issues = []
        strengths = []

        # Verificar estructura según tipo de contenido
        structure_score = self.evaluate_content_structure(content, text_type)
        score += structure_score["score"] * 0.4

        # Verificar lenguaje institucional apropiado
        institutional_language = self.check_institutional_language(content, category)
        score += institutional_language["score"] * 0.3

        # Verificar contexto mexicano
        mexican_context = self.check_mexican_context(content)
        score += mexican_context["score"] * 0.3

        # Consolidar fortalezas y problemas
        strengths.extend(structure_score.get("strengths", []))
        strengths.extend(institutional_language.get("strengths", []))
        strengths.extend(mexican_context.get("strengths", []))

        issues.extend(structure_score.get("issues", []))
        issues.extend(institutional_language.get("issues", []))
        issues.extend(mexican_context.get("issues", []))

        return {
            "score": min(score, 100),
            "issues": issues,
            "strengths": strengths,
            "details": f"Estructura: {structure_score['score']:.1f}, Lenguaje: {institutional_language['score']:.1f}, Contexto: {mexican_context['score']:.1f}"
        }

    def evaluate_content_structure(self, content: str, text_type: str) -> Dict:
        """Evalúa estructura específica por tipo de contenido"""
        score = 0
        issues = []
        strengths = []

        paragraphs = content.split('\n\n')
        sentences = content.split('.')

        if text_type == "Nota Periodística":
            # Verificar pirámide invertida
            first_paragraph = paragraphs[0] if paragraphs else ""

            # Verificar elementos 5W en primer párrafo
            w_elements = ['qué', 'quién', 'cuándo', 'dónde']
            w_found = sum(1 for w in w_elements if w in first_paragraph.lower())

            if w_found >= 3:
                score += 40
                strengths.append("Lead incluye elementos informativos clave (5W)")
            else:
                issues.append("Lead no incluye suficientes elementos básicos (qué, quién, cuándo, dónde)")

            # Verificar longitud apropiada
            if len(paragraphs) <= 4:
                score += 30
                strengths.append("Longitud apropiada para nota periodística")
            else:
                issues.append("Nota demasiado extensa para formato breve")

            # Verificar cierre sin conclusión editorial
            last_paragraph = paragraphs[-1] if paragraphs else ""
            editorial_conclusions = ["en conclusión", "por tanto", "finalmente", "para concluir"]
            has_editorial_conclusion = any(phrase in last_paragraph.lower() for phrase in editorial_conclusions)

            if not has_editorial_conclusion:
                score += 30
                strengths.append("Cierre factual sin conclusión editorial")
            else:
                issues.append("Evitar conclusiones editoriales en notas informativas")

        elif text_type == "Artículo":
            # Verificar presencia de subtítulos o secciones
            if len(paragraphs) >= 3:
                score += 30
                strengths.append("Estructura extendida apropiada para artículo")
            else:
                issues.append("Artículo requiere mayor desarrollo y secciones")

            # Verificar conclusión informativa
            last_paragraph = paragraphs[-1] if paragraphs else ""
            if len(last_paragraph) > 50:
                score += 35
                strengths.append("Incluye conclusión desarrollada")
            else:
                issues.append("Falta conclusión que resuma hallazgos")

            score += 35  # Base score for article format

        elif text_type == "Guión de TV":
            # Verificar oraciones cortas
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

            if avg_sentence_length <= 15:
                score += 40
                strengths.append("Oraciones apropiadas para lectura oral")
            else:
                issues.append("Oraciones demasiado largas para formato televisivo")

            # Verificar indicaciones técnicas
            technical_indicators = ["(VIDEO:", "(AUDIO:", "(GRÁFICO:", "SOT"]
            tech_found = sum(1 for indicator in technical_indicators if indicator in content)

            if tech_found >= 1:
                score += 30
                strengths.append("Incluye indicaciones técnicas apropiadas")
            else:
                issues.append("Falta indicaciones técnicas para producción TV")

            score += 30  # Base score for TV script

        elif text_type == "Crónica":
            # Verificar elementos narrativos
            narrative_elements = ["describe", "observa", "relata", "cuenta", "narra"]
            narrative_found = sum(1 for element in narrative_elements if element in content.lower())

            if narrative_found >= 2:
                score += 40
                strengths.append("Incluye elementos narrativos apropiados")
            else:
                issues.append("Falta desarrollo narrativo característico de crónica")

            # Verificar diálogos o citas integradas
            dialogue_count = len(re.findall(r'"[^"]{20,}"', content))
            if dialogue_count >= 2:
                score += 30
                strengths.append("Incluye diálogos/citas integradas naturalmente")
            else:
                issues.append("Falta citas o diálogos integrados en narrativa")

            score += 30  # Base score for chronicle

        return {
            "score": min(score, 100),
            "issues": issues,
            "strengths": strengths
        }

    def check_institutional_language(self, content: str, category: str) -> Dict:
        """Verifica uso de lenguaje institucional apropiado"""
        score = 70  # Base score
        issues = []
        strengths = []

        # Verificar formalidad apropiada
        informal_words = ["súper", "mega", "wow", "increíble", "genial"]
        informal_found = sum(1 for word in informal_words if word in content.lower())

        if informal_found == 0:
            score += 15
            strengths.append("Mantiene registro formal apropiado")
        else:
            issues.append("Evitar lenguaje informal o coloquial")
            score -= 10

        # Verificar neutralidad (ausencia de adjetivos valorativos no atribuidos)
        non_attributed_opinions = ["excelente", "terrible", "magnífico", "pésimo", "fantástico"]
        opinion_found = sum(1 for opinion in non_attributed_opinions if opinion in content.lower())

        if opinion_found == 0:
            score += 15
            strengths.append("Mantiene neutralidad sin juicios no atribuidos")
        else:
            issues.append("Evitar adjetivos valorativos sin atribución")
            score -= 15

        return {
            "score": min(max(score, 0), 100),
            "issues": issues,
            "strengths": strengths
        }

    def check_mexican_context(self, content: str) -> Dict:
        """Verifica presencia apropiada de contexto mexicano"""
        score = 0
        issues = []
        strengths = []

        # Contar indicadores de contexto mexicano
        context_count = sum(1 for indicator in self.mexican_context_indicators
                          if indicator.lower() in content.lower())

        if context_count >= 3:
            score += 50
            strengths.append("Fuerte contexto mexicano")
        elif context_count >= 1:
            score += 30
            strengths.append("Incluye contexto mexicano")
        else:
            issues.append("Falta contextualización para audiencia mexicana")

        # Verificar mención de impacto en población
        impact_indicators = ["afecta", "impacto", "beneficia", "ciudadanos", "familias", "mexicanos"]
        impact_count = sum(1 for indicator in impact_indicators if indicator in content.lower())

        if impact_count >= 2:
            score += 50
            strengths.append("Explica impacto en población mexicana")
        else:
            issues.append("Falta explicación de impacto en audiencia objetivo")

        return {
            "score": min(score, 100),
            "issues": issues,
            "strengths": strengths,
            "details": f"Contexto mexicano: {context_count}, Impacto: {impact_count}"
        }

    def evaluate_audience_relevance(self, content: str, category: str) -> Dict:
        """Evalúa relevancia para audiencia mexicana"""
        score = 0
        issues = []
        strengths = []

        # Verificar información útil para ciudadanos
        utility_indicators = [
            "cómo acceder", "requisitos", "dónde solicitar", "cuándo inicia",
            "qué significa para", "impacto en", "beneficio para"
        ]

        utility_count = sum(1 for indicator in utility_indicators if indicator in content.lower())

        if utility_count >= 2:
            score += 40
            strengths.append("Proporciona información práctica útil")
        elif utility_count >= 1:
            score += 25
        else:
            issues.append("Falta información práctica para ciudadanos")

        # Verificar explicación de términos técnicos
        technical_terms = ["PIB", "inflación", "tipo de cambio", "aranceles", "vinculación a proceso"]
        technical_found = sum(1 for term in technical_terms if term in content)

        if technical_found > 0:
            # Verificar si hay explicaciones cerca
            explained_count = 0
            for term in technical_terms:
                if term in content:
                    term_index = content.find(term)
                    context = content[max(0, term_index-50):term_index+100]
                    if any(phrase in context.lower() for phrase in ["es decir", "significa", "se refiere a", "consiste en"]):
                        explained_count += 1

            if explained_count >= technical_found * 0.7:  # 70% explained
                score += 35
                strengths.append("Explica apropiadamente términos técnicos")
            else:
                issues.append("Falta explicación de algunos términos técnicos")
                score += 15
        else:
            score += 25  # No technical terms, no issues

        # Verificar actualidad y oportunidad
        timeliness_indicators = ["hoy", "ayer", "esta semana", "reciente", "actual", "ahora"]
        timeliness_found = any(indicator in content.lower() for indicator in timeliness_indicators)

        if timeliness_found:
            score += 25
            strengths.append("Contenido actual y oportuno")
        else:
            issues.append("Falta indicación de actualidad o relevancia temporal")

        return {
            "score": min(score, 100),
            "issues": issues,
            "strengths": strengths,
            "details": f"Utilidad práctica: {utility_count}, Términos técnicos: {technical_found}"
        }

    def evaluate_information_completeness(self, content: str, text_type: str) -> Dict:
        """Evalúa completitud de información (5W+H)"""
        score = 0
        issues = []
        strengths = []

        # Verificar las 5W + H
        completeness_elements = {
            'qué': ['qué', 'cuál', 'cómo'],
            'quién': ['quién', 'quien', 'presidente', 'secretario', 'director', 'ministro'],
            'cuándo': ['cuándo', 'cuando', 'fecha', 'ayer', 'hoy', 'enero', 'febrero', 'marzo'],
            'dónde': ['dónde', 'donde', 'México', 'Ciudad de México', 'estado', 'país'],
            'por_qué': ['por qué', 'porque', 'debido', 'causa', 'razón', 'motivo'],
            'cómo': ['cómo', 'como', 'manera', 'forma', 'método', 'proceso']
        }

        covered_elements = []
        for element, indicators in completeness_elements.items():
            if any(indicator.lower() in content.lower() for indicator in indicators):
                covered_elements.append(element)

        coverage_percentage = len(covered_elements) / 6
        score += coverage_percentage * 60

        if len(covered_elements) >= 5:
            strengths.append("Excelente cobertura de elementos informativos (5W+H)")
        elif len(covered_elements) >= 4:
            strengths.append("Buena cobertura de elementos básicos")
        else:
            issues.append("Falta información básica (quién, qué, cuándo, dónde, por qué, cómo)")

        # Verificar contexto y antecedentes (específico para Once Noticias)
        context_indicators = ["antecedente", "contexto", "desde", "anteriormente", "históricamente"]
        has_context = any(indicator in content.lower() for indicator in context_indicators)

        if has_context:
            score += 20
            strengths.append("Incluye contexto y antecedentes")
        else:
            if text_type in ["Artículo", "Crónica"]:
                issues.append("Falta contexto histórico o antecedentes")

        # Verificar perspectivas futuras (valorado en Once Noticias)
        future_indicators = ["futuro", "próximo", "esperado", "proyección", "se espera", "planea"]
        has_future_perspective = any(indicator in content.lower() for indicator in future_indicators)

        if has_future_perspective:
            score += 20
            strengths.append("Incluye perspectivas futuras")
        else:
            if text_type == "Artículo":
                issues.append("Falta perspectiva o proyecciones futuras")

        return {
            "score": min(score, 100),
            "issues": issues,
            "strengths": strengths,
            "details": f"Elementos cubiertos: {', '.join(covered_elements)}"
        }

    def evaluate_editorial_identity(self, content: str) -> Dict:
        """Evalúa adherencia a identidad editorial Once Noticias"""
        score = 80  # Base score
        issues = []
        strengths = []

        # Verificar tono de servicio público
        service_indicators = ["ciudadanos", "población", "beneficio", "servicio", "información", "apoyo"]
        service_count = sum(1 for indicator in service_indicators if indicator in content.lower())

        if service_count >= 2:
            strengths.append("Refleja enfoque de servicio público")
        else:
            issues.append("Fortalecer enfoque de servicio público")
            score -= 10

        # Verificar ausencia de sensacionalismo
        sensationalist_words = ["impactante", "shock", "escándalo", "bombazo", "exclusiva"]
        sensationalism_found = sum(1 for word in sensationalist_words if word in content.lower())

        if sensationalism_found == 0:
            strengths.append("Mantiene sobriedad sin sensacionalismo")
        else:
            issues.append("Evitar lenguaje sensacionalista")
            score -= 15

        # Verificar balance institucional
        if "gobierno" in content.lower() or "presidente" in content.lower():
            # Verificar si hay equilibrio o al menos objetividad
            critical_balance = ["sin embargo", "por otro lado", "mientras que", "no obstante"]
            has_balance = any(phrase in content.lower() for phrase in critical_balance)

            if has_balance:
                strengths.append("Mantiene equilibrio informativo")
                score += 10
            else:
                # No necesariamente malo, pero verificar objetividad
                if "celebró" in content or "destacó" in content:
                    strengths.append("Reporta declaraciones oficiales objetivamente")

        return {
            "score": min(max(score, 0), 100),
            "issues": issues,
            "strengths": strengths
        }

    def evaluate_once_noticias_compliance(self, content: str, text_type: str, category: str) -> Dict:
        """Evaluación específica de cumplimiento con estilo Once Noticias"""
        compliance = {
            "title_analysis": {},
            "lead_analysis": {},
            "attribution_patterns": {},
            "category_specific": {},
            "overall_style_match": 0
        }

        lines = content.split('\n')
        title = lines[0] if lines else ""

        # Análisis de título
        compliance["title_analysis"] = self.analyze_title_once_style(title)

        # Análisis de lead/apertura
        paragraphs = content.split('\n\n')
        lead = paragraphs[0] if paragraphs else ""
        compliance["lead_analysis"] = self.analyze_lead_once_style(lead, text_type)

        # Análisis de patrones de atribución
        compliance["attribution_patterns"] = self.analyze_attribution_patterns(content)

        # Análisis específico por categoría
        compliance["category_specific"] = self.analyze_category_compliance(content, category)

        # Score general de cumplimiento
        scores = [
            compliance["title_analysis"].get("score", 0),
            compliance["lead_analysis"].get("score", 0),
            compliance["attribution_patterns"].get("score", 0),
            compliance["category_specific"].get("score", 0)
        ]
        compliance["overall_style_match"] = sum(scores) / len(scores) if scores else 0

        return compliance

    def analyze_title_once_style(self, title: str) -> Dict:
        """Analiza título según estándares Once Noticias"""
        score = 0
        issues = []
        strengths = []

        title_length = len(title)
        if 20 <= title_length <= 80:
            score += 30
            strengths.append("Longitud de título apropiada")
        else:
            issues.append(f"Título {'muy largo' if title_length > 80 else 'muy corto'} para estándares Once Noticias")

        # Verificar datos específicos en título
        if re.search(r'\d+(?:\.\d+)?(?:%|por ciento|millones?|mil)', title):
            score += 35
            strengths.append("Título incluye datos específicos")
        else:
            issues.append("Considerar incluir datos específicos en título")

        # Verificar claridad y especificidad
        vague_terms = ["algunos", "varios", "muchos", "pocos"]
        if any(term in title.lower() for term in vague_terms):
            issues.append("Evitar términos vagos en títulos")
        else:
            score += 35
            strengths.append("Título específico y claro")

        return {
            "score": min(score, 100),
            "issues": issues,
            "strengths": strengths
        }

    def analyze_lead_once_style(self, lead: str, text_type: str) -> Dict:
        """Analiza lead/apertura según estilo Once Noticias"""
        score = 0
        issues = []
        strengths = []

        if text_type == "Nota Periodística":
            # Verificar patrón típico Once Noticias
            once_patterns = [
                r"(?:La|El)\s+(?:presidenta?|secretari[oa]|fiscal)\s+.*?\s+(?:celebró|anunció|informó|señaló)\s+que",
                r"(?:La|El)\s+(?:Fiscalía|Secretaría|Senado).*?(?:obtuvo|logró|reportó|confirmó)"
            ]

            pattern_match = any(re.search(pattern, lead, re.IGNORECASE) for pattern in once_patterns)

            if pattern_match:
                score += 40
                strengths.append("Sigue patrón de apertura típico Once Noticias")
            else:
                issues.append("No sigue patrones de apertura característicos de Once Noticias")

            # Verificar inclusión de fuente en primera oración
            source_in_lead = any(source in lead for source in ["según", "de acuerdo con", "informó", "INEGI", "Banxico"])

            if source_in_lead:
                score += 30
                strengths.append("Incluye atribución de fuente en lead")
            else:
                issues.append("Falta atribución de fuente en primera oración")

            # Verificar contexto integrado
            context_indicators = ["desde", "el nivel más", "por primera vez", "segundo"]
            has_context = any(indicator in lead.lower() for indicator in context_indicators)

            if has_context:
                score += 30
                strengths.append("Integra contexto en apertura")
            else:
                issues.append("Falta contexto temporal o comparativo en lead")

        return {
            "score": min(score, 100),
            "issues": issues,
            "strengths": strengths
        }

    def analyze_attribution_patterns(self, content: str) -> Dict:
        """Analiza patrones de atribución específicos Once Noticias"""
        score = 0
        issues = []
        strengths = []

        # Contar patrones de atribución típicos
        attribution_count = 0
        for pattern in self.attribution_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            attribution_count += len(matches)

        if attribution_count >= 2:
            score += 50
            strengths.append("Usa múltiples patrones de atribución característicos")
        elif attribution_count >= 1:
            score += 30
            strengths.append("Usa patrones de atribución apropiados")
        else:
            issues.append("No usa patrones de atribución típicos de Once Noticias")

        # Verificar verbos declarativos específicos
        declarative_verbs = ["informó", "señaló", "anunció", "celebró", "confirmó", "destacó", "advirtió"]
        verb_count = sum(1 for verb in declarative_verbs if verb in content.lower())

        if verb_count >= 2:
            score += 50
            strengths.append("Emplea verbos declarativos variados")
        elif verb_count >= 1:
            score += 30
        else:
            issues.append("Falta variedad en verbos declarativos")

        return {
            "score": min(score, 100),
            "issues": issues,
            "strengths": strengths,
            "details": f"Patrones de atribución: {attribution_count}, Verbos declarativos: {verb_count}"
        }

    def analyze_category_compliance(self, content: str, category: str) -> Dict:
        """Analiza cumplimiento específico por categoría"""
        score = 70  # Base score
        issues = []
        strengths = []

        category_requirements = self.category_patterns.get(category, {})

        if category == "Economía":
            # Verificar presencia de cifras específicas
            numbers_pattern = r'\d+(?:\.\d+)?(?:\s*(?:por ciento|%|millones?|mil|pesos))?'
            numbers_found = len(re.findall(numbers_pattern, content))

            if numbers_found >= 3:
                score += 15
                strengths.append("Incluye múltiples datos económicos específicos")

            # Verificar fuentes económicas oficiales
            econ_sources = ["INEGI", "Banxico", "SHCP"]
            sources_found = sum(1 for source in econ_sources if source in content)

            if sources_found >= 1:
                score += 15
                strengths.append("Cita fuentes económicas oficiales apropiadas")
            else:
                issues.append("Falta citación de fuentes económicas oficiales (INEGI, Banxico, SHCP)")

        elif category == "Política":
            # Verificar cargos completos en primera mención
            political_figures = re.findall(r'(?:presidente|presidenta|secretari[oa]|senador|diputad[oa])\s+[A-Z][a-z]+', content)

            if political_figures:
                score += 15
                strengths.append("Menciona cargos políticos apropiadamente")

            # Verificar equilibrio si hay controversia
            controversy_indicators = ["crítica", "oposición", "rechazo", "controversia"]
            balance_indicators = ["por su parte", "mientras que", "sin embargo"]

            has_controversy = any(indicator in content.lower() for indicator in controversy_indicators)
            has_balance = any(indicator in content.lower() for indicator in balance_indicators)

            if has_controversy and has_balance:
                score += 15
                strengths.append("Mantiene equilibrio en temas controversiales")
            elif has_controversy and not has_balance:
                issues.append("Considerar incluir múltiples perspectivas en temas controversiales")

        elif category == "Justicia":
            # Verificar terminología jurídica precisa
            legal_terms = ["vinculación a proceso", "sentencia condenatoria", "delitos", "prisión preventiva"]
            legal_found = sum(1 for term in legal_terms if term in content.lower())

            if legal_found >= 1:
                score += 15
                strengths.append("Usa terminología jurídica precisa")

            # Verificar enumeración de evidencias
            evidence_pattern = r'\d+\s+(?:armas|cargadores|cartuchos|kilogramos|personas)'
            evidence_found = len(re.findall(evidence_pattern, content))

            if evidence_found >= 2:
                score += 15
                strengths.append("Detalla evidencias con precisión")

        return {
            "score": min(score, 100),
            "issues": issues,
            "strengths": strengths
        }

    def calculate_weighted_score(self, detailed_scores: Dict) -> float:
        """Calcula score ponderado según importancia de criterios"""
        total_score = 0
        total_weight = 0

        for criterion, score_data in detailed_scores.items():
            if criterion in self.editorial_standards:
                weight = self.editorial_standards[criterion]["weight"]
                score = score_data.get("score", 0)
                total_score += score * (weight / 100)
                total_weight += weight

        return (total_score / total_weight * 100) if total_weight > 0 else 0

    def determine_publication_readiness(self, evaluation: Dict) -> bool:
        """Determina si el contenido está listo para publicación en Once Noticias"""
        overall_score = evaluation.get("overall_score", 0)
        critical_issues = []

        # Criterios mínimos para publicación Once Noticias
        for criterion, data in evaluation["detailed_scores"].items():
            if data.get("score", 0) < 60:  # Score mínimo por criterio
                critical_issues.extend(data.get("issues", []))

        # Debe tener score general >= 75 Y cumplimiento estilo >= 70
        style_compliance = evaluation.get("once_noticias_compliance", {}).get("overall_style_match", 0)

        evaluation["critical_issues"] = critical_issues

        return overall_score >= 75 and style_compliance >= 70 and len(critical_issues) <= 2

    def generate_specific_recommendations(self, evaluation: Dict, text_type: str, category: str) -> List[str]:
        """Genera recomendaciones específicas para mejorar el contenido"""
        recommendations = []
        overall_score = evaluation.get("overall_score", 0)

        if overall_score < 75:
            recommendations.append("🔴 PRIORITY: Revisión editorial completa necesaria antes de publicación")

        # Recomendaciones específicas por criterios débiles
        for criterion, data in evaluation["detailed_scores"].items():
            if data.get("score", 0) < 70:
                recommendations.append(f"⚠️ {criterion.replace('_', ' ').title()}: {'; '.join(data.get('issues', []))}")

        # Recomendaciones específicas de estilo Once Noticias
        style_compliance = evaluation.get("once_noticias_compliance", {})

        if style_compliance.get("overall_style_match", 0) < 70:
            recommendations.append("📝 Revisar adherencia al estilo editorial de Once Noticias")

            # Recomendaciones específicas por componente
            for component, data in style_compliance.items():
                if isinstance(data, dict) and data.get("score", 0) < 70:
                    recommendations.extend(f"• {component}: {issue}" for issue in data.get("issues", []))

        # Recomendaciones específicas por tipo de contenido y categoría
        if text_type == "Nota Periodística" and overall_score < 80:
            recommendations.append("📋 Verificar pirámide invertida y elementos 5W en primer párrafo")

        if category in ["Economía", "Política", "Justicia"] and overall_score < 80:
            recommendations.append(f"🎯 Revisar fuentes y terminología específica para {category}")

        # Recomendaciones positivas si el score es alto
        if overall_score >= 85:
            recommendations.append("✅ Contenido de alta calidad, listo para publicación Once Noticias")
            strengths = []
            for data in evaluation["detailed_scores"].values():
                strengths.extend(data.get("strengths", []))
            if strengths:
                recommendations.append(f"💪 Fortalezas principales: {'; '.join(strengths[:3])}")

        return recommendations

    def improve_training_data_quality(self, training_data: List[Dict]) -> List[Dict]:
        """
        Mejora la calidad de los datos de entrenamiento según estándares Once Noticias
        """
        improved_data = []
        quality_stats = {"total": len(training_data), "approved": 0, "rejected": 0}

        for item in training_data:
            if "text" in item and "metadata" in item:
                evaluation = self.evaluate_content_quality(item["text"], item["metadata"])

                # Criterios más estrictos para datos de entrenamiento
                if evaluation["overall_score"] > 80 and evaluation["publication_ready"]:
                    item["quality_score"] = evaluation["overall_score"]
                    item["quality_evaluation"] = evaluation
                    item["once_noticias_compliance"] = evaluation["once_noticias_compliance"]
                    improved_data.append(item)
                    quality_stats["approved"] += 1
                else:
                    quality_stats["rejected"] += 1

        # Agregar estadísticas de mejora
        improvement_ratio = quality_stats["approved"] / quality_stats["total"] if quality_stats["total"] > 0 else 0

        return {
            "improved_data": improved_data,
            "statistics": quality_stats,
            "improvement_ratio": improvement_ratio,
            "recommendations": [
                f"Se mantuvieron {quality_stats['approved']} ejemplos de {quality_stats['total']} ({improvement_ratio:.1%})",
                "Ejemplos aprobados cumplen estándares editoriales Once Noticias",
                "Se recomienda generar más ejemplos específicos por categoría si ratio < 70%"
            ]
        }