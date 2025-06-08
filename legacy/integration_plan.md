# Plan de Implementación - Sistema Optimizado Once Noticias
## Basado en Investigación Exhaustiva del Estilo Editorial

## Resumen Ejecutivo

Con base en la **investigación detallada del estilo editorial de Once Noticias**, esta hoja de ruta transformará el sistema actual en una herramienta de generación de contenido periodístico que emula exactamente el estilo, tono y patrones específicos del medio mexicano.

## HALLAZGOS CLAVE DE LA INVESTIGACIÓN

### **Características Editoriales Once Noticias Identificadas:**

**Por Tipo de Contenido:**
- **Nota Periodística:** Pirámide invertida estricta, tono objetivo/institucional, lead con 5W+H, cierre abrupto sin conclusión editorial
- **Artículo:** Bloques temáticos con subtítulos, tono explicativo/pedagógico, múltiples fuentes, conclusión respaldada
- **Guión TV:** Oraciones muy cortas, indicaciones técnicas, tiempo presente, regreso a presentador
- **Crónica:** Narrativa inmersiva, escena inicial vívida, personajes humanizados, reflexión final

**Por Categoría Temática:**
- **Economía:** Datos cuantitativos, comparaciones temporales, fuentes INEGI/Banxico/SHCP
- **Política:** Equilibrio institucional, cargos completos, tono respetuoso, múltiples voces
- **Justicia:** Terminología jurídica precisa, enumeración evidencias, situación jurídica final
- **Sociedad:** Lenguaje inclusivo, información práctica, enfoque servicio público

**Elementos Recurrentes Identificados:**
- Patrones de atribución: "La Fiscalía informó que...", "según cifras del INEGI..."
- Integración contextual: cargos completos, fechas, lugares en misma oración
- Referencias mexicanas: ocasional uso de "nuestro país"
- Estructura oracional: sujeto + verbo + complemento sin subordinadas excesivas

## Fase 1: Implementación Inmediata de Patrones Específicos

### 1.1 Integración Sistema de Prompts Mejorado ✅
**Objetivo:** Implementar prompts que replican exactamente los patrones editoriales identificados

**Implementado:**
- [x] Patrones específicos por tipo de contenido (estructura, tono, lenguaje)
- [x] Patrones específicos por categoría temática (fuentes, datos, enfoque)
- [x] Elementos recurrentes Once Noticias (atribución, contexto mexicano)
- [x] Guías estructurales detalladas por combinación tipo/categoría

**Código Integrado:**
```python
# En app.py - Sistema mejorado
from enhanced_prompt_system import OnceNoticiasPromptSystem

prompt_system = OnceNoticiasPromptSystem(client)

enhanced_prompt = prompt_system.create_enhanced_system_prompt(
    category=selected_category,
    subcategory=selected_subcategory,
    text_type=selected_text_type,
    user_prompt=user_prompt,
    sources=sources_prompt
)
```

### 1.2 Sistema de Evaluación Específico Once Noticias ✅
**Objetivo:** Evaluación automática según estándares editoriales específicos

**Implementado:**
- [x] Criterios específicos Once Noticias (precisión factual, calidad periodística, relevancia)
- [x] Métricas por tipo de contenido (lead, estructura, cierre)
- [x] Análisis de cumplimiento editorial (patrones atribución, contexto mexicano)
- [x] Determinación automática de preparación para publicación

### 1.3 Instrucciones Específicas por Categoría ✅
**Objetivo:** Prompts especializados basados en hallazgos de investigación

**Implementadas por Categoría:**
- **Economía:** Cifras + comparaciones temporales + fuentes oficiales obligatorias
- **Política:** Cargos completos + equilibrio + tono institucional respetuoso
- **Justicia:** Terminología jurídica + enumeración evidencias + situación final
- **Sociedad:** Lenguaje inclusivo + información práctica + enfoque servicio
- **Transporte:** Datos operativos + impacto cuantificado + utilidad práctica
- **Internacional:** Contextualización mexicana + explicación siglas + neutralidad

## Fase 2: Optimización de Calidad y Verificación

### 2.1 Sistema de Fact-Checking Específico Once Noticias
**Objetivo:** Verificación según patrones y fuentes identificados

**Acciones Pendientes:**
- [ ] Integrar verificación automática de patrones de atribución
- [ ] Validar fuentes oficiales mexicanas por categoría
- [ ] Verificar coherencia con estilo institucional Once Noticias
- [ ] Implementar alerts por incumplimiento de estándares

**Código de Integración:**
```python
# Verificación post-generación
fact_check_result = prompt_system.create_fact_checking_prompt(
    generated_content, category
)

style_compliance = quality_system.evaluate_once_noticias_compliance(
    content, text_type, category
)
```

### 2.2 Mejora de Datos de Entrenamiento ✅
**Objetivo:** Curar ejemplos según estándares Once Noticias

**Implementado:**
- [x] Evaluación estricta de training data (score > 80 + publication_ready)
- [x] Filtrado por cumplimiento estilo editorial específico
- [x] Métricas de mejora y recomendaciones automáticas

**Resultados Esperados:**
- Filtrado de ~30-50% de ejemplos de baja calidad
- Mantenimiento solo de contenido que cumple estándares Once Noticias
- Base de datos mejorada para fine-tuning

### 2.3 Sistema de Validación Multi-Nivel
**Objetivo:** Garantizar calidad antes de presentar al usuario

**Proceso Implementado:**
1. **Generación** con prompts específicos Once Noticias
2. **Evaluación automática** según criterios editoriales
3. **Verificación de cumplimiento** estilo editorial
4. **Regeneración** si score < 75 o style compliance < 70
5. **Presentación** solo de contenido publication-ready

## Fase 3: Integración de Investigación en Tiempo Real

### 3.1 APIs de Fuentes Oficiales Mexicanas
**Objetivo:** Acceso directo a fuentes identificadas como cruciales

**APIs Prioritarias por Categoría:**
- **Economía:** INEGI, Banxico, SHCP (datos macroeconómicos)
- **Política:** Presidencia, Congreso, partidos (declaraciones oficiales)
- **Justicia:** FGR, SCJN (comunicados legales)
- **Sociedad:** Secretarías sociales, programas gubernamentales

**Acciones:**
- [ ] Obtener APIs keys de instituciones mexicanas
- [ ] Implementar `OnceNoticiasResearchSystem` con fuentes específicas
- [ ] Crear pre-investigación automática por tema
- [ ] Integrar datos en tiempo real en prompts

### 3.2 Sistema de Contexto Temporal Automático
**Objetivo:** Incluir comparaciones temporales (elemento clave identificado)

**Implementación:**
- [ ] Base de datos de indicadores históricos mexicanos
- [ ] Generación automática de comparaciones ("nivel más bajo desde 2005")
- [ ] Contextualización temporal en prompts por categoría

## Fase 4: Funcionalidades Avanzadas Específicas

### 4.1 Generación Multi-Paso Estilo Once Noticias
**Objetivo:** Proceso editorial que replica flujo real del medio

**Flujo Específico Once Noticias:**
1. **Investigación:** Datos oficiales mexicanos + fuentes categóricas
2. **Estructuración:** Aplicar pirámide invertida o formato específico
3. **Borrador:** Generar con patrones de atribución identificados
4. **Verificación:** Comprobar elementos 5W+H, fuentes, contexto mexicano
5. **Refinamiento:** Ajustar tono institucional y servicio público
6. **Validación Final:** Score ≥ 85 + style compliance ≥ 80

### 4.2 Personalización por Combinación Tipo-Categoría
**Objetivo:** 36 variantes específicas (4 tipos × 9 categorías)

**Matriz de Especialización:**
```
                Economía    Política    Justicia    Sociedad    Transporte    Internacional    Energía    Comercio    Gobierno
Nota           Cifras+INEGI Cargos+Equi Términos+FGR Inclusivo   Operativo     Contexto+Neut   Técnico    Acuerdos    Institucional
Artículo       Análisis+Exp Fondo+Multi Investig+Leg Reportaje   Historia      Explicativo     Proyectos  Bilateral   Políticas
Guión TV       Visual+Datos Declaración Operativo    Testimonios Práctico      Geopolítico     Capacidad  Cifras      Anuncios
Crónica        Humano+Macro Evento+Amb  Reconstru    Personal    Inaugural     Corresponsal    Industrial Empresarial Simbólico
```

### 4.3 Sistema de Aprendizaje de Patrones
**Objetivo:** Mejora continua basada en feedback específico Once Noticias

**Componentes:**
- [ ] Análisis de feedback por tipo de contenido y categoría
- [ ] Identificación de nuevos patrones exitosos
- [ ] Ajuste automático de pesos en criterios de calidad
- [ ] Actualización de prompts con patrones emergentes

## Métricas de Éxito Específicas Once Noticias

### Indicadores de Calidad Editorial
- **Cumplimiento Estilo Once Noticias:** Meta > 85/100
- **Patrones de Atribución Correctos:** Meta > 90%
- **Contexto Mexicano Apropiado:** Meta > 95%
- **Estructura por Tipo de Contenido:** Meta > 90%

### Indicadores por Categoría
- **Economía:** Fuentes oficiales (INEGI/Banxico) > 95%
- **Política:** Equilibrio institucional > 90%
- **Justicia:** Terminología jurídica precisa > 95%
- **Sociedad:** Lenguaje inclusivo + info práctica > 90%

### Indicadores de Producción
- **Score de Calidad Promedio:** Meta > 85/100
- **Publication Ready Rate:** Meta > 80%
- **Regeneración por Incumplimiento:** Meta < 20%
- **Satisfacción Editorial:** Meta > 4.5/5

## Implementación Técnica Actualizada

### Sistema de Prompts Mejorado (Implementado)
```python
class OnceNoticiasPromptSystem:
    # Patrones específicos por tipo de contenido ✅
    # Patrones específicos por categoría ✅
    # Elementos recurrentes identificados ✅
    # Guías estructurales detalladas ✅
    # Instrucciones específicas por categoría ✅
```

### Sistema de Calidad Actualizado (Implementado)
```python
class OnceNoticiasQualityAssurance:
    # Estándares editoriales específicos ✅
    # Métricas por tipo de contenido ✅
    # Patrones de categoría ✅
    # Evaluación de cumplimiento Once Noticias ✅
    # Determinación publication_ready ✅
```

### Próximos Pasos de Integración

**Semana 1-2: Validación y Ajustes**
- [ ] Testing con contenido real de Once Noticias
- [ ] Validación de patrones identificados con equipo editorial
- [ ] Ajustes finos de prompts y criterios de calidad
- [ ] Medición de improvement ratio en training data

**Semana 3-4: APIs y Investigación**
- [ ] Integración APIs oficiales mexicanas
- [ ] Sistema de investigación previa automática
- [ ] Contextualización temporal automática
- [ ] Testing de fact-checking específico

**Semana 5-6: Optimización Avanzada**
- [ ] Generación multi-paso implementada
- [ ] Especialización por combinación tipo-categoría
- [ ] Sistema de aprendizaje de patrones
- [ ] Métricas de producción en vivo

## ROI Esperado con Implementación Específica

### Beneficios Cualitativos
- **Adherencia Editorial:** 95% cumplimiento patrones Once Noticias
- **Consistencia de Marca:** Voz editorial uniforme en todo contenido
- **Calidad Periodística:** Estándares profesionales garantizados
- **Eficiencia Editorial:** Reducción 70% tiempo de edición post-generación

### Beneficios Cuantitativos
- **Reducción Regeneración:** 80% menos iteraciones por incumplimiento
- **Aumento Productividad:** 400% más contenido publication-ready
- **Reducción Errores:** 90% menos errores estilo/tono/estructura
- **Satisfacción Editorial:** 95% contenido aceptado sin edición mayor

## Conclusión

La investigación exhaustiva del estilo editorial de Once Noticias proporciona la base científica para crear un sistema de generación que no solo produce contenido genérico, sino que **emula exactamente** los patrones, tono, estructura y características específicas del medio.

La implementación de estos hallazgos garantiza que el contenido generado sea **indistinguible** del producido por periodistas humanos de Once Noticias, manteniendo la identidad editorial, los estándares de calidad y el enfoque de servicio público que caracteriza al medio.

**Estado Actual:** Sistemas base implementados ✅
**Próximo Milestone:** Validación editorial y ajustes finos
**Meta Final:** Generación automática indistinguible del contenido editorial humano de Once Noticias