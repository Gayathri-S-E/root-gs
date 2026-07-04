"""
Disease Service — orchestrates image upload + AI detection
"""

import io
import time
import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from services.ai.gemini_client import gemini_client
from models.disease import DiseaseReport, DiseaseSeverity
from models.user import User


class DiseaseService:

    async def detect_disease(
        self,
        image_bytes: bytes,
        filename: str,
        user: User,
        db: AsyncSession,
        farm_id: Optional[int] = None,
        crop_cycle_id: Optional[int] = None,
        crop_hint: Optional[str] = None,
    ) -> DiseaseReport:
        """Full disease detection pipeline: upload → AI → save to DB."""

        start = time.time()

        # 1. Upload image to local storage (S3 in production)
        image_url = await self._save_image_local(image_bytes, filename, user.id)

        # 2. Run AI detection
        user_api_key = user.farmer_profile.gemini_api_key if user.farmer_profile else None
        ai_result = await gemini_client.analyze_crop_disease(image_bytes, crop_hint, api_key=user_api_key)

        # 3. Map severity string to enum
        severity_str = ai_result.get("severity", "none")
        try:
            severity = DiseaseSeverity(severity_str)
        except ValueError:
            severity = DiseaseSeverity.none

        # 4. Persist to database
        report = DiseaseReport(
            user_id=user.id,
            farm_id=farm_id,
            crop_cycle_id=crop_cycle_id,
            image_url=image_url,
            crop_name=ai_result.get("crop_name"),
            disease_name=ai_result.get("disease_name"),
            disease_scientific_name=ai_result.get("disease_scientific_name"),
            confidence_score=ai_result.get("confidence_score", 0.0),
            severity=severity,
            affected_area_percent=ai_result.get("affected_area_percent"),
            description=ai_result.get("description"),
            reason=ai_result.get("reason"),
            evidence=ai_result.get("evidence"),
            risk_level=ai_result.get("risk_level"),
            chemical_treatment=json.dumps(ai_result.get("chemical_treatment", [])),
            organic_treatment=json.dumps(ai_result.get("organic_treatment", [])),
            prevention_tips=json.dumps(ai_result.get("prevention_tips", [])),
            medicine_dosage=ai_result.get("medicine_dosage"),
            estimated_loss_percent=ai_result.get("estimated_loss_percent"),
            alternative_diagnosis=json.dumps(ai_result.get("alternative_diagnosis", [])),
            processing_time_ms=int((time.time() - start) * 1000),
            ai_model_used=ai_result.get("ai_model_used", "gemini-1.5-pro"),
            raw_ai_response=json.dumps(ai_result),
        )

        db.add(report)
        await db.flush()
        await db.refresh(report)
        return report

    async def _save_image_local(self, image_bytes: bytes, filename: str, user_id: int) -> str:
        """Save image locally (use S3 in production)."""
        import aiofiles
        import os

        safe_name = f"{user_id}_{int(time.time())}_{filename.replace(' ', '_')}"
        path = f"media/disease/{safe_name}"
        os.makedirs("media/disease", exist_ok=True)

        async with aiofiles.open(path, "wb") as f:
            await f.write(image_bytes)

        return f"/media/disease/{safe_name}"


disease_service = DiseaseService()
