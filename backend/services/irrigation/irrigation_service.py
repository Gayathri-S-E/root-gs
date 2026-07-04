"""
Smart Irrigation Service — Water requirement calculation
"""

from typing import Optional
from loguru import logger


# Water requirement per crop stage (mm/day)
CROP_WATER_NEEDS = {
    "rice": {"sowing": 6, "vegetative": 8, "flowering": 10, "harvesting": 4},
    "wheat": {"sowing": 4, "vegetative": 5, "flowering": 7, "harvesting": 3},
    "maize": {"sowing": 4, "vegetative": 6, "flowering": 8, "harvesting": 3},
    "cotton": {"sowing": 5, "vegetative": 7, "flowering": 9, "harvesting": 4},
    "sugarcane": {"sowing": 6, "vegetative": 8, "flowering": 10, "harvesting": 5},
    "tomato": {"sowing": 4, "vegetative": 5, "flowering": 7, "harvesting": 4},
    "potato": {"sowing": 4, "vegetative": 6, "flowering": 7, "harvesting": 3},
    "onion": {"sowing": 3, "vegetative": 5, "flowering": 6, "harvesting": 3},
    "default": {"sowing": 4, "vegetative": 6, "flowering": 7, "harvesting": 3},
}

# Soil moisture retention factor
SOIL_FACTORS = {
    "clay": 1.2,
    "loamy": 1.0,
    "sandy": 0.7,
    "silty": 0.9,
    "clay_loam": 1.1,
    "peaty": 0.8,
    "chalky": 0.75,
}

# Irrigation efficiency
IRRIGATION_EFFICIENCY = {
    "drip": 0.95,
    "sprinkler": 0.80,
    "flood": 0.60,
    "furrow": 0.65,
    "rainfed": 1.0,
    "none": 1.0,
}


class IrrigationService:

    def calculate_schedule(
        self,
        crop_name: str,
        area_acres: float,
        soil_type: str,
        irrigation_type: str,
        current_stage: str,
        last_irrigation_days: int = 0,
        rainfall_last_7_days_mm: float = 0,
    ) -> dict:
        """Calculate irrigation schedule and water requirements."""

        crop_key = crop_name.lower()
        water_map = CROP_WATER_NEEDS.get(crop_key, CROP_WATER_NEEDS["default"])
        stage_key = current_stage.lower() if current_stage.lower() in water_map else "vegetative"

        # Base water need (mm/day)
        base_need_mm = water_map[stage_key]

        # Adjust for soil type
        soil_factor = SOIL_FACTORS.get(soil_type.lower(), 1.0)
        adjusted_need = base_need_mm * soil_factor

        # Account for recent rainfall
        effective_rainfall = min(rainfall_last_7_days_mm / 7, adjusted_need)
        net_need = max(0, adjusted_need - effective_rainfall)

        # Days since last irrigation — should we irrigate now?
        ideal_frequency = self._get_ideal_frequency(crop_key, stage_key, soil_type)
        should_irrigate = last_irrigation_days >= ideal_frequency

        # Liters per acre (1mm on 1 acre = 4046.86 liters)
        liters_per_acre = net_need * 4046.86
        total_liters = liters_per_acre * area_acres

        # Adjust for irrigation system efficiency
        efficiency = IRRIGATION_EFFICIENCY.get(irrigation_type.lower(), 0.75)
        gross_water_liters = total_liters / efficiency

        # Water saving score (higher = more efficient)
        water_saving_score = efficiency * 100 * (1 - (net_need / (base_need_mm * soil_factor + 0.001))) * 0.5 + efficiency * 50

        tips = self._get_water_saving_tips(irrigation_type, crop_key, soil_type)

        # Generate daily schedule
        from datetime import date, timedelta
        today = date.today()
        daily_schedule = []
        for i in range(7):
            day = today + timedelta(days=i)
            irrigate = (i % ideal_frequency == 0 and i > 0) or (i == 0 and should_irrigate)
            daily_schedule.append({
                "date": day.isoformat(),
                "irrigate": irrigate,
                "water_liters": round(total_liters, 1) if irrigate else 0,
                "time": "06:00 AM (recommended)" if irrigate else None,
            })

        return {
            "recommended": should_irrigate,
            "water_required_liters": round(total_liters, 1),
            "gross_water_required_liters": round(gross_water_liters, 1),
            "next_irrigation_date": (today + timedelta(days=max(0, ideal_frequency - last_irrigation_days))).isoformat(),
            "frequency_days": ideal_frequency,
            "method": irrigation_type,
            "reason": f"{crop_name} in {current_stage} stage requires {net_need:.1f}mm water/day. "
                     f"Your {soil_type} soil retains water well. "
                     f"{'Rainfall has reduced water needs.' if effective_rainfall > 0 else 'No recent rainfall — irrigation needed.'}",
            "confidence": 0.82,
            "daily_schedule": daily_schedule,
            "water_saving_tips": tips,
            "water_saving_score": round(min(water_saving_score, 100), 1),
        }

    def _get_ideal_frequency(self, crop: str, stage: str, soil: str) -> int:
        """Returns days between irrigation events."""
        base = {"sowing": 3, "vegetative": 5, "flowering": 4, "harvesting": 7}.get(stage, 5)
        if soil == "sandy":
            base -= 1
        elif soil in ["clay", "clay_loam"]:
            base += 1
        return max(1, base)

    def _get_water_saving_tips(self, irrigation_type: str, crop: str, soil: str) -> list:
        tips = [
            "Irrigate in early morning (5–7 AM) to minimize evaporation",
            "Mulch your fields to retain soil moisture",
            "Check soil moisture before irrigating — don't irrigate wet soil",
        ]
        if irrigation_type == "flood":
            tips.append("Consider upgrading to drip irrigation — saves 50–70% water")
            tips.append("Level your field to ensure uniform water distribution")
        if irrigation_type == "drip":
            tips.append("Check drip emitters for clogging weekly")
            tips.append("Fertigation through drip system improves efficiency")
        if soil == "sandy":
            tips.append("Sandy soil drains fast — irrigate more frequently in smaller amounts")
        return tips


irrigation_service = IrrigationService()
