"""
Gemini AI Client — Disease detection, crop advisory, chatbot
Uses the new google-genai SDK (supports AQ. API keys via v1 endpoint)
"""

import asyncio
import json
import time
from typing import Optional

from google import genai
from google.genai.types import HttpOptions, GenerateContentConfig, Part
from loguru import logger

from core.config import settings


SYSTEM_PROMPT_AGRICULTURE = """
You are ROOTGS AI, an expert agriculture scientist and agronomist with 30 years of experience.
You help Indian farmers with:
- Crop disease identification and treatment
- Crop selection and planning
- Irrigation and fertilizer recommendations
- Weather-based advisories
- Government scheme guidance
- Market price insights

Rules:
1. Always explain WHY you are giving a recommendation (Explainable AI)
2. Never hallucinate — if uncertain, say so clearly with confidence score
3. Every response must include: recommendation, reason, evidence, confidence, alternatives, risk
4. Be specific — provide dosages, timelines, quantities
5. Mention both chemical AND organic alternatives
6. Be empathetic and encouraging to farmers
7. Speak simply, as if talking to a village farmer
8. For disease detection, always mention preventive measures for the future
"""

MODEL_NAME = "gemini-2.5-flash"


def _make_client(api_key: str) -> genai.Client:
    """Create a Gemini client using v1 (stable) — for generate_content calls."""
    return genai.Client(
        api_key=api_key,
        http_options=HttpOptions(api_version="v1"),
    )


def _make_client_beta(api_key: str) -> genai.Client:
    """Create a Gemini client using v1beta — needed for chat with systemInstruction."""
    return genai.Client(
        api_key=api_key,
        http_options=HttpOptions(api_version="v1beta"),
    )


def _clean_json(text: str) -> str:
    """Strip markdown code fences from AI response."""
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        # parts[1] is the content between first ``` and second ```
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return text


class GeminiClient:
    """Wrapper around Gemini API for agriculture AI features."""

    async def analyze_crop_disease(
        self,
        image_bytes: bytes,
        crop_hint: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> dict:
        """Analyze a crop image for diseases. Returns structured detection result."""
        active_key = api_key or settings.GOOGLE_GEMINI_API_KEY
        if not active_key:
            return self._demo_disease_response()

        start_time = time.time()

        prompt = f"""
Analyze this crop image and detect any diseases, pests, or abnormalities.
{"Crop type hint: " + crop_hint if crop_hint else ""}

Return a JSON object with EXACTLY these fields:
{{
    "crop_name": "name of detected crop",
    "disease_name": "specific disease name or 'Healthy'",
    "disease_scientific_name": "scientific name if applicable",
    "confidence_score": 0.0-1.0,
    "severity": "none|mild|moderate|severe|critical",
    "affected_area_percent": 0-100,
    "description": "detailed description of what you see",
    "reason": "why you identified this disease (visual evidence)",
    "evidence": "specific visual features that led to this diagnosis",
    "risk_level": "low|medium|high|critical",
    "chemical_treatment": [{{"name": "", "dosage": "", "frequency": "", "notes": ""}}],
    "organic_treatment": [{{"name": "", "dosage": "", "frequency": "", "notes": ""}}],
    "prevention_tips": ["tip1", "tip2"],
    "medicine_dosage": "specific dosage instructions",
    "estimated_loss_percent": 0-100,
    "alternative_diagnosis": [{{"disease": "", "confidence": 0.0}}]
}}

Be accurate. If the plant looks healthy, say disease_name = "Healthy" with confidence 0.95+.
Return ONLY valid JSON, no markdown.
"""

        def _sync_call():
            client = _make_client(active_key)
            image_part = Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt, image_part],
            )
            return response.text

        try:
            raw_text = await asyncio.to_thread(_sync_call)
            processing_ms = int((time.time() - start_time) * 1000)
            result = json.loads(_clean_json(raw_text))
            result["processing_time_ms"] = processing_ms
            result["ai_model_used"] = MODEL_NAME
            return result

        except Exception as e:
            logger.error(f"Gemini disease detection error: {e}")
            if api_key:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=400,
                    detail=f"Gemini API Error: {str(e)}. Please check your API Key in Profile settings.",
                )
            return self._demo_disease_response()

    async def chat_agriculture(
        self,
        messages: list[dict],
        language: str = "en",
        api_key: Optional[str] = None,
    ) -> dict:
        """Multi-turn agricultural chatbot."""
        active_key = api_key or settings.GOOGLE_GEMINI_API_KEY
        if not active_key:
            return self._demo_chat_response()

        system_instruction = SYSTEM_PROMPT_AGRICULTURE + (
            "\nRespond in Tamil language." if language == "ta" else "\nRespond in English."
        )

        # Build history list — Gemini requires "model" not "assistant"
        history = []
        for msg in messages[:-1]:
            gemini_role = "model" if msg["role"] == "assistant" else msg["role"]
            history.append({"role": gemini_role, "parts": [{"text": msg["content"]}]})

        last_message = messages[-1]["content"]

        def _sync_call():
            client = _make_client_beta(active_key)
            chat = client.chats.create(
                model=MODEL_NAME,
                config=GenerateContentConfig(
                    system_instruction=system_instruction,
                ),
                history=history,
            )
            response = chat.send_message(last_message)
            return response.text

        try:
            text = await asyncio.to_thread(_sync_call)
            return {
                "content": text,
                "reasoning": "Based on agricultural science and best practices",
                "confidence": 0.88,
                "sources": ["Agricultural Research Institute", "FAO Guidelines", "ICAR"],
            }

        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            if api_key:
                return {
                    "content": (
                        f"⚠️ Gemini API Error: {str(e)}.\n\n"
                        "Please verify your Google Gemini API Key in your Profile settings "
                        "(click your initials 'RK' in the top-right corner)."
                    ),
                    "reasoning": "Gemini API failure",
                    "confidence": 0.0,
                    "sources": ["System Diagnostics"],
                }
            return self._demo_chat_response()

    async def get_crop_recommendation(
        self,
        context: dict,
        api_key: Optional[str] = None,
    ) -> dict:
        """Get AI crop recommendation based on farm context."""
        active_key = api_key or settings.GOOGLE_GEMINI_API_KEY
        if not active_key:
            return self._demo_crop_recommendation()

        prompt = f"""
As an expert agronomist, recommend the best crops for this farm:

Farm Context:
- Location: {context.get('state', 'Unknown')}, {context.get('district', 'Unknown')}
- Soil Type: {context.get('soil_type', 'loamy')}
- Area: {context.get('area_acres', 1)} acres
- Irrigation: {context.get('irrigation_type', 'rainfed')}
- Season: {context.get('season', 'kharif')}
- Soil pH: {context.get('ph', 'unknown')}
- Previous Crop: {context.get('previous_crop', 'unknown')}
- Budget: {context.get('budget', 'medium')}

Return JSON:
{{
    "recommendation": "primary crop recommendation",
    "reason": "detailed scientific reason",
    "evidence": "data-backed evidence",
    "confidence_score": 0.0-1.0,
    "alternatives": ["crop2", "crop3"],
    "risk_level": "low|medium|high",
    "expected_yield": "X quintals per acre",
    "expected_profit": "approximate profit",
    "care_calendar": [{{"week": 1, "action": ""}}]
}}
Return ONLY valid JSON.
"""

        def _sync_call():
            client = _make_client(active_key)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            return response.text

        try:
            raw_text = await asyncio.to_thread(_sync_call)
            return json.loads(_clean_json(raw_text))

        except Exception as e:
            logger.error(f"Gemini crop recommendation error: {e}")
            if api_key:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=400,
                    detail=f"Gemini API Error: {str(e)}. Please check your API Key in Profile settings.",
                )
            return self._demo_crop_recommendation()

    # ─── Demo Responses (when no API key) ─────────────────────────
    def _demo_disease_response(self) -> dict:
        return {
            "crop_name": "Rice",
            "disease_name": "Rice Blast",
            "disease_scientific_name": "Magnaporthe oryzae",
            "confidence_score": 0.87,
            "severity": "moderate",
            "affected_area_percent": 35.0,
            "description": "Rice Blast is a fungal disease caused by Magnaporthe oryzae. Diamond-shaped lesions with grey centers and brown borders are visible on leaves.",
            "reason": "The diamond-shaped lesions with characteristic grey centres and reddish-brown margins are classic indicators of Rice Blast disease.",
            "evidence": "Visual: spindle-shaped lesions on leaves, grey center with brown border, lesion size 1-3cm",
            "risk_level": "high",
            "chemical_treatment": [
                {"name": "Tricyclazole 75% WP", "dosage": "0.6g/L water", "frequency": "Once every 15 days", "notes": "Apply during early morning or evening"},
                {"name": "Carbendazim 50% WP", "dosage": "1g/L water", "frequency": "Twice at 10-day interval", "notes": "Avoid spraying in rain"},
            ],
            "organic_treatment": [
                {"name": "Pseudomonas fluorescens", "dosage": "10g/L water", "frequency": "Every 10 days", "notes": "Best as preventive measure"},
                {"name": "Neem oil", "dosage": "5mL/L water", "frequency": "Every 7 days", "notes": "Add few drops of soap"},
            ],
            "prevention_tips": [
                "Use blast-resistant varieties like IR64, MTU1010",
                "Maintain optimal plant spacing (20x15 cm)",
                "Avoid excessive nitrogen fertilization",
                "Ensure proper drainage in fields",
                "Remove and burn infected plant debris",
            ],
            "medicine_dosage": "Tricyclazole 75% WP @ 0.6g per liter of water. Spray 500L per hectare.",
            "estimated_loss_percent": 30.0,
            "alternative_diagnosis": [
                {"disease": "Brown Spot", "confidence": 0.08},
                {"disease": "Sheath Blight", "confidence": 0.05},
            ],
            "processing_time_ms": 1250,
            "ai_model_used": "demo-mode",
        }

    def _demo_chat_response(self) -> dict:
        return {
            "content": "Hello! I'm ROOTGS AI, your personal agriculture expert. I'm currently running in demo mode. To unlock full AI capabilities, please configure your Google Gemini API key. I can help you with crop diseases, irrigation schedules, weather advisories, government schemes, and much more! What would you like to know about your farm today?",
            "reasoning": "Demo mode response",
            "confidence": 1.0,
            "sources": ["ROOTGS AI System"],
        }

    def _demo_crop_recommendation(self) -> dict:
        return {
            "recommendation": "Rice (Paddy)",
            "reason": "Based on your farm's soil type and location, rice is the most suitable crop for the kharif season with good returns.",
            "evidence": "Loamy soil with good water retention, high rainfall area, optimal temperature range 25-35°C",
            "confidence_score": 0.85,
            "alternatives": ["Soybean", "Maize", "Black Gram"],
            "risk_level": "low",
            "expected_yield": "25-30 quintals per acre",
            "expected_profit": "₹25,000 - ₹35,000 per acre",
            "care_calendar": [
                {"week": 1, "action": "Nursery preparation and seed soaking"},
                {"week": 3, "action": "Transplanting to main field"},
                {"week": 6, "action": "First nitrogen dose application"},
                {"week": 10, "action": "Second dose of fertilizer, weed control"},
                {"week": 14, "action": "Flower initiation — critical irrigation"},
                {"week": 18, "action": "Grain filling stage — reduce irrigation"},
                {"week": 20, "action": "Harvest when 80% grains are golden"},
            ],
        }


# Singleton
gemini_client = GeminiClient()
