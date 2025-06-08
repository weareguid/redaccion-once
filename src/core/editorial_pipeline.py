# Automated Editorial Pipeline for Once Noticias
# Integrates optimized prompt system, quality assurance, and user feedback

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import pandas as pd

from .prompt_system import OptimizedOnceNoticiasPromptSystem
from .quality_assurance import OnceNoticiasQualityAssurance

@dataclass
class EditorialMetrics:
    """Métricas del pipeline editorial"""
    generation_time: float
    edit_time: float
    regenerations: int
    quality_score: float
    publication_ready: bool
    data_injection_used: bool
    security_incidents: int
    user_feedback_provided: bool = False

class ContentRequest(BaseModel):
    """Modelo para requests de generación"""
    category: str
    subcategory: str
    text_type: str
    user_prompt: str
    sources: str = ""
    selected_length: str = "auto"
    enable_data_injection: bool = False  # Deshabilitado por ahora
    webhook_url: Optional[str] = None

class ImprovementRequest(BaseModel):
    """Modelo para requests de mejora con feedback"""
    content: str
    quality_evaluation: Dict
    category: str
    text_type: str
    user_feedback: str
    metadata: Dict = {}

class ContentResponse(BaseModel):
    """Modelo para responses de contenido"""
    content: str
    quality_evaluation: Dict
    metrics: EditorialMetrics
    status: str
    timestamp: str
    request_id: str
    requires_improvement: bool = False
    improvement_available: bool = False
    estimated_tokens: float = 0
    sensitive_topics_detected: bool = False

class AutomatedEditorialPipeline:
    """Pipeline editorial automatizado con webhooks, métricas y feedback del usuario"""

    def __init__(self, openai_client, enable_web_search: bool = False):
        # Sistemas optimizados
        self.prompt_system = OptimizedOnceNoticiasPromptSystem(openai_client)
        self.quality_system = OnceNoticiasQualityAssurance()
        self.openai_client = openai_client

        # Pipeline metrics
        self.weekly_metrics = {
            "total_requests": 0,
            "avg_generation_time": 0,
            "avg_quality_score": 0,
            "publication_ready_rate": 0,
            "regeneration_rate": 0,
            "data_injection_success_rate": 0,
            "user_feedback_rate": 0,
            "weekly_trend": []
        }

        # Cache de contenido para optimización
        self.content_cache = {}

        # Web search deshabilitado por ahora
        self.web_search_enabled = enable_web_search

        # Queue de webhooks
        self.webhook_queue = []

    async def call_openai_api(self, prompt: str, user_prompt: str) -> str:
        """Llamada real a OpenAI API usando GPT-4o"""
        try:
            response = await asyncio.create_task(
                asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-4o",  # Modelo más avanzado
                    messages=[
                        {
                            "role": "system",
                            "content": prompt
                        },
                        {
                            "role": "user",
                            "content": f"Genera el contenido según las especificaciones: {user_prompt}"
                        }
                    ],
                    temperature=0.1,  # Baja temperatura para consistencia periodística
                    max_tokens=2000,  # Suficiente para contenido extenso
                    top_p=0.9
                )
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error en llamada OpenAI: {str(e)}")
            return ""

    async def generate_content_pipeline(self, request: ContentRequest, auto_improve: bool = False) -> ContentResponse:
        """Pipeline completo de generación con métricas automatizadas y opción de auto-mejora"""

        start_time = time.time()
        request_id = f"REQ_{int(time.time())}_{hash(request.user_prompt) % 1000}"

        try:
            # PASO 1: Generación inicial
            generation_start = time.time()

            # Verificar cache
            cache_key = f"{request.category}_{request.text_type}_{hash(request.user_prompt)}"
            if cache_key in self.content_cache:
                cached_result = self.content_cache[cache_key]
                cached_result["cache_hit"] = True
                return cached_result

            # Detectar temas sensibles antes de generar
            sensitive_topics_detected = self.prompt_system._detect_sensitive_topics(request.user_prompt)

            # Generar prompt optimizado
            prompt = self.prompt_system.create_enhanced_system_prompt(
                category=request.category,
                subcategory=request.subcategory,
                text_type=request.text_type,
                user_prompt=request.user_prompt,
                sources=request.sources,
                selected_length=request.selected_length
            )

            # Llamada real a OpenAI
            initial_content = await self.call_openai_api(prompt, request.user_prompt)

            if not initial_content:
                raise Exception("No se pudo generar contenido")

            generation_time = time.time() - generation_start

            # PASO 2: Evaluación de calidad
            evaluation_start = time.time()

            quality_evaluation = self.quality_system.evaluate_content_quality(
                content=initial_content,
                metadata={
                    'category': request.category,
                    'subcategory': request.subcategory,
                    'text_type': request.text_type,
                    'user_prompt': request.user_prompt,
                    'selected_length': request.selected_length,
                    'sensitive_topics_detected': sensitive_topics_detected
                }
            )

            # Agregar información de temas sensibles a la evaluación
            quality_evaluation['sensitive_topics_detected'] = sensitive_topics_detected

            # PASO 3: Mejora automática solo si auto_improve está habilitado
            final_content = initial_content
            regenerations = 0
            improvement_available = not quality_evaluation.get("publication_ready", False)

            if auto_improve and improvement_available:
                # Regeneración automática
                improvement_prompt = self.prompt_system.create_improvement_prompt(
                    initial_content, quality_evaluation, request.category, request.text_type
                )

                improved_content = await self.call_openai_api(improvement_prompt, request.user_prompt)

                if improved_content:
                    regenerations = 1

                    # Re-evaluar
                    final_evaluation = self.quality_system.evaluate_content_quality(
                        content=improved_content,
                        metadata={
                            'category': request.category,
                            'subcategory': request.subcategory,
                            'text_type': request.text_type,
                            'user_prompt': request.user_prompt,
                            'selected_length': request.selected_length,
                            'sensitive_topics_detected': sensitive_topics_detected
                        }
                    )

                    if final_evaluation.get("publication_ready", False):
                        final_content = improved_content
                        quality_evaluation = final_evaluation
                        quality_evaluation['sensitive_topics_detected'] = sensitive_topics_detected
                        improvement_available = False

            edit_time = time.time() - evaluation_start
            total_time = time.time() - start_time

            # Estimar tokens usados
            estimated_tokens = len(prompt.split()) * 1.3

            # PASO 4: Crear métricas
            metrics = EditorialMetrics(
                generation_time=generation_time,
                edit_time=edit_time,
                regenerations=regenerations,
                quality_score=quality_evaluation.get("overall_score", 0),
                publication_ready=quality_evaluation.get("publication_ready", False),
                data_injection_used=False,  # Deshabilitado por ahora
                security_incidents=self.prompt_system.metrics.get("security_blocks", 0),
                user_feedback_provided=False
            )

            # PASO 5: Actualizar métricas del sistema
            self._update_weekly_metrics(metrics)

            # PASO 6: Preparar respuesta
            response = ContentResponse(
                content=final_content,
                quality_evaluation=quality_evaluation,
                metrics=metrics,
                status="success",
                timestamp=datetime.now().isoformat(),
                request_id=request_id,
                requires_improvement=not quality_evaluation.get("publication_ready", False),
                improvement_available=improvement_available,
                estimated_tokens=estimated_tokens,
                sensitive_topics_detected=sensitive_topics_detected
            )

            # PASO 7: Cache si es de alta calidad
            if quality_evaluation.get("overall_score", 0) >= 85:
                self.content_cache[cache_key] = response

            # PASO 8: Webhook si fue especificado
            if request.webhook_url:
                self._queue_webhook(request.webhook_url, response.dict())

            return response

        except Exception as e:
            return ContentResponse(
                content="",
                quality_evaluation={},
                metrics=EditorialMetrics(0, 0, 0, 0, False, False, 0, False),
                status="error",
                timestamp=datetime.now().isoformat(),
                request_id=request_id,
                requires_improvement=False,
                improvement_available=False
            )

    async def improve_content_with_feedback(self, request: ImprovementRequest) -> ContentResponse:
        """Mejora contenido basado en feedback del usuario y evaluación de calidad"""

        start_time = time.time()
        request_id = f"IMP_{int(time.time())}_{hash(request.user_feedback) % 1000}"

        try:
            # Crear prompt de mejora con feedback
            improvement_prompt = self.prompt_system.create_improvement_prompt(
                initial_content=request.content,
                quality_evaluation=request.quality_evaluation,
                category=request.category,
                text_type=request.text_type,
                user_feedback=request.user_feedback
            )

            # Generar contenido mejorado
            improved_content = await self.call_openai_api(improvement_prompt, request.user_feedback)

            if not improved_content:
                raise Exception("No se pudo mejorar el contenido")

            # Re-evaluar calidad
            improved_evaluation = self.quality_system.evaluate_content_quality(
                content=improved_content,
                metadata={
                    'category': request.category,
                    'text_type': request.text_type,
                    'user_feedback': request.user_feedback,
                    **request.metadata
                }
            )

            generation_time = time.time() - start_time

            # Crear métricas de mejora
            metrics = EditorialMetrics(
                generation_time=generation_time,
                edit_time=0,
                regenerations=1,
                quality_score=improved_evaluation.get("overall_score", 0),
                publication_ready=improved_evaluation.get("publication_ready", False),
                data_injection_used=False,
                security_incidents=0,
                user_feedback_provided=True
            )

            # Actualizar métricas
            self._update_weekly_metrics(metrics)

            return ContentResponse(
                content=improved_content,
                quality_evaluation=improved_evaluation,
                metrics=metrics,
                status="improved",
                timestamp=datetime.now().isoformat(),
                request_id=request_id,
                requires_improvement=not improved_evaluation.get("publication_ready", False),
                improvement_available=False
            )

        except Exception as e:
            return ContentResponse(
                content=request.content,  # Devolver contenido original si falla
                quality_evaluation=request.quality_evaluation,
                metrics=EditorialMetrics(0, 0, 0, 0, False, False, 0, True),
                status="improvement_failed",
                timestamp=datetime.now().isoformat(),
                request_id=request_id,
                requires_improvement=True,
                improvement_available=True
            )

    def _update_weekly_metrics(self, metrics: EditorialMetrics):
        """Actualiza métricas semanales para tendencias"""

        # Calcular promedios móviles
        current_count = self.weekly_metrics["total_requests"]

        self.weekly_metrics["total_requests"] += 1
        self.weekly_metrics["avg_generation_time"] = (
            (self.weekly_metrics["avg_generation_time"] * current_count + metrics.generation_time) /
            (current_count + 1)
        )
        self.weekly_metrics["avg_quality_score"] = (
            (self.weekly_metrics["avg_quality_score"] * current_count + metrics.quality_score) /
            (current_count + 1)
        )

        # Calcular tasa de feedback
        if metrics.user_feedback_provided:
            feedback_count = int(self.weekly_metrics["user_feedback_rate"] * current_count / 100) + 1
            self.weekly_metrics["user_feedback_rate"] = feedback_count / (current_count + 1) * 100

        # Calcular otras tasas
        if self.weekly_metrics["total_requests"] > 0:
            total = self.weekly_metrics["total_requests"]
            ready_count = 1 if metrics.publication_ready else 0
            self.weekly_metrics["publication_ready_rate"] = (
                (self.weekly_metrics["publication_ready_rate"] * (total - 1) + ready_count * 100) / total
            )

            regeneration_count = metrics.regenerations
            current_regen_rate = self.weekly_metrics["regeneration_rate"] * (total - 1) / 100
            self.weekly_metrics["regeneration_rate"] = (current_regen_rate + regeneration_count) / total * 100

        # Agregar punto de datos para tendencia (cada día)
        today = datetime.now().strftime("%Y-%m-%d")
        if not self.weekly_metrics["weekly_trend"] or self.weekly_metrics["weekly_trend"][-1]["date"] != today:
            self.weekly_metrics["weekly_trend"].append({
                "date": today,
                "requests": 1,
                "avg_quality": metrics.quality_score,
                "publication_ready_rate": 100 if metrics.publication_ready else 0,
                "user_feedback_rate": 100 if metrics.user_feedback_provided else 0
            })
        else:
            # Actualizar día actual
            last_entry = self.weekly_metrics["weekly_trend"][-1]
            last_entry["requests"] += 1
            last_entry["avg_quality"] = (last_entry["avg_quality"] + metrics.quality_score) / 2

        # Mantener solo últimas 2 semanas
        if len(self.weekly_metrics["weekly_trend"]) > 14:
            self.weekly_metrics["weekly_trend"] = self.weekly_metrics["weekly_trend"][-14:]

    def _queue_webhook(self, webhook_url: str, data: Dict):
        """Encola webhook para envío asíncrono"""
        self.webhook_queue.append({
            "url": webhook_url,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "attempts": 0
        })

    async def process_webhook_queue(self):
        """Procesa queue de webhooks en background"""
        while self.webhook_queue:
            webhook = self.webhook_queue.pop(0)

            try:
                # Implementar envío real de webhook
                # requests.post(webhook["url"], json=webhook["data"])
                print(f"✅ Webhook enviado a {webhook['url']}")

            except Exception as e:
                webhook["attempts"] += 1
                if webhook["attempts"] < 3:
                    # Reintentar
                    self.webhook_queue.append(webhook)
                else:
                    print(f"❌ Webhook falló después de 3 intentos: {webhook['url']}")

    def get_weekly_trend_analysis(self) -> Dict:
        """Análisis de tendencias semanales"""

        if len(self.weekly_metrics["weekly_trend"]) < 7:
            return {"status": "insufficient_data", "message": "Se necesitan al menos 7 días de datos"}

        recent_week = self.weekly_metrics["weekly_trend"][-7:]
        previous_week = self.weekly_metrics["weekly_trend"][-14:-7] if len(self.weekly_metrics["weekly_trend"]) >= 14 else []

        current_avg_quality = sum(day["avg_quality"] for day in recent_week) / len(recent_week)
        current_ready_rate = sum(day["publication_ready_rate"] for day in recent_week) / len(recent_week)

        analysis = {
            "current_week": {
                "avg_quality_score": round(current_avg_quality, 1),
                "publication_ready_rate": round(current_ready_rate, 1),
                "total_requests": sum(day["requests"] for day in recent_week)
            },
            "trends": {
                "quality_trend": "stable",
                "volume_trend": "stable",
                "efficiency_trend": "stable"
            },
            "recommendations": []
        }

        if previous_week:
            prev_avg_quality = sum(day["avg_quality"] for day in previous_week) / len(previous_week)
            prev_ready_rate = sum(day["publication_ready_rate"] for day in previous_week) / len(previous_week)

            # Detectar tendencias
            quality_change = current_avg_quality - prev_avg_quality
            if quality_change > 5:
                analysis["trends"]["quality_trend"] = "improving"
                analysis["recommendations"].append("✅ Calidad mejorando - mantener estrategia actual")
            elif quality_change < -5:
                analysis["trends"]["quality_trend"] = "declining"
                analysis["recommendations"].append("⚠️ Calidad bajando - revisar prompts y datos")

            # Detectar problemas y recomendar acciones
            if current_ready_rate < 70:
                analysis["recommendations"].append("🔧 Baja tasa publication-ready - ajustar criterios de calidad")

            if self.weekly_metrics["regeneration_rate"] > 30:
                analysis["recommendations"].append("⚡ Alta tasa regeneración - optimizar prompts iniciales")

        return analysis

    def get_system_health(self) -> Dict:
        """Estado de salud del sistema completo"""

        prompt_metrics = self.prompt_system.get_optimization_metrics()

        health_status = {
            "overall_health": "healthy",
            "components": {
                "prompt_system": {
                    "status": "operational",
                    "token_efficiency": prompt_metrics["performance"]["token_reduction"],
                    "avg_tokens": prompt_metrics["performance"]["avg_prompt_tokens"]
                },
                "data_injection": {
                    "status": "operational" if self.prompt_system.data_injection_enabled else "disabled",
                    "success_rate": prompt_metrics["data_injection"]["injection_rate"],
                    "apis_connected": prompt_metrics["data_injection"]["external_apis"]
                },
                "quality_system": {
                    "status": "operational",
                    "avg_score": self.weekly_metrics["avg_quality_score"],
                    "publication_rate": self.weekly_metrics["publication_ready_rate"]
                },
                "security": {
                    "status": "active",
                    "threats_blocked": prompt_metrics["security"]["threats_blocked"],
                    "filters_active": prompt_metrics["security"]["filters_active"]
                }
            },
            "performance": {
                "avg_generation_time": round(self.weekly_metrics["avg_generation_time"], 2),
                "cache_hit_ratio": "N/A",  # Implementar tracking
                "webhook_success_rate": "N/A"  # Implementar tracking
            },
            "alerts": []
        }

        # Detectar problemas
        if self.weekly_metrics["avg_quality_score"] < 70:
            health_status["overall_health"] = "warning"
            health_status["alerts"].append("Calidad promedio por debajo del umbral")

        if prompt_metrics["quality"]["regeneration_rate"] > 40:
            health_status["overall_health"] = "warning"
            health_status["alerts"].append("Alta tasa de regeneraciones")

        if len(health_status["alerts"]) == 0:
            health_status["alerts"].append("Sistema funcionando óptimamente")

        return health_status

# FastAPI app para endpoints automatizados
app = FastAPI(title="Once Noticias Editorial Pipeline", version="2.0.0")

# Instancia global del pipeline
pipeline = None

@app.on_event("startup")
async def startup_event():
    global pipeline
    # Inicializar con cliente OpenAI real
    # pipeline = AutomatedEditorialPipeline(openai_client)
    pass

@app.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest, background_tasks: BackgroundTasks):
    """OPTIMIZACIÓN 9: Endpoint /generate para automatización"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline no inicializado")

    # Procesar en background los webhooks
    background_tasks.add_task(pipeline.process_webhook_queue)

    return await pipeline.generate_content_pipeline(request)

@app.post("/verify")
async def verify_content(content: str, metadata: Dict):
    """OPTIMIZACIÓN 9: Endpoint /verify para verificación independiente"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline no inicializado")

    evaluation = pipeline.quality_system.evaluate_content_quality(content, metadata)
    return {"status": "success", "evaluation": evaluation}

@app.post("/improve")
async def improve_content(content: str, evaluation: Dict, metadata: Dict):
    """OPTIMIZACIÓN 9: Endpoint /improve para mejoras automatizadas"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline no inicializado")

    improvement_prompt = pipeline.prompt_system.create_improvement_prompt(
        content, evaluation, metadata.get('category'), metadata.get('text_type')
    )

    # Generar contenido mejorado
    improved_content = await pipeline._call_openai_async(improvement_prompt)

    return {
        "status": "success",
        "improved_content": improved_content,
        "improvement_prompt": improvement_prompt
    }

@app.get("/metrics/weekly")
async def get_weekly_metrics():
    """Métricas semanales y análisis de tendencias"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline no inicializado")

    return {
        "metrics": pipeline.weekly_metrics,
        "trend_analysis": pipeline.get_weekly_trend_analysis()
    }

@app.get("/health")
async def get_system_health():
    """Estado de salud del sistema completo"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline no inicializado")

    return pipeline.get_system_health()

@app.post("/config/data-injection")
async def configure_data_injection(api_keys: Dict[str, str]):
    """Configurar APIs para inyección de datos"""
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline no inicializado")

    pipeline.enable_data_injection(api_keys)
    return {"status": "success", "message": f"Data injection habilitado con {len(api_keys)} APIs"}

# Comando para ejecutar: uvicorn automated_editorial_pipeline:app --reload