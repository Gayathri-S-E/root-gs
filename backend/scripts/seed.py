"""
Seed script to populate initial crop database, government schemes, and market prices
"""
import asyncio
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import AsyncSessionLocal, engine
from core.security import hash_password
from models.user import User, FarmerProfile, UserRole
from models.crop import Crop, CropSeason
from models.analytics import GovernmentScheme, MarketPrice
from models.farm import Farm, SoilType, IrrigationType

async def seed_data():
    print("🌱 Starting database seeding...")
    
    # Auto-create tables if they don't exist
    from models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables verified/created.")

    async with AsyncSessionLocal() as db:
        # 1. Seed crops if empty
        result = await db.execute(select(Crop))
        if not result.scalars().first():
            print("🌾 Seeding master crops database...")
            crops = [
                Crop(
                    name="Rice (Paddy)",
                    local_name="Nel / Paddy",
                    scientific_name="Oryza sativa",
                    category="cereal",
                    season=CropSeason.kharif,
                    water_requirement_mm=800,
                    growth_days=120,
                    ideal_temp_min=20.0,
                    ideal_temp_max=35.0,
                    ideal_ph_min=5.5,
                    ideal_ph_max=6.5,
                    avg_yield_per_acre=25.0,
                    description="Rice is the staple food crop of a majority of the people in India.",
                    image_url="/media/crops/rice.jpg"
                ),
                Crop(
                    name="Wheat",
                    local_name="Godhumai / Wheat",
                    scientific_name="Triticum aestivum",
                    category="cereal",
                    season=CropSeason.rabi,
                    water_requirement_mm=450,
                    growth_days=130,
                    ideal_temp_min=10.0,
                    ideal_temp_max=25.0,
                    ideal_ph_min=6.0,
                    ideal_ph_max=7.5,
                    avg_yield_per_acre=20.0,
                    description="Wheat is the second most important cereal crop in India.",
                    image_url="/media/crops/wheat.jpg"
                ),
                Crop(
                    name="Tomato",
                    local_name="Thakkali / Tomato",
                    scientific_name="Solanum lycopersicum",
                    category="vegetable",
                    season=CropSeason.zaid,
                    water_requirement_mm=600,
                    growth_days=90,
                    ideal_temp_min=15.0,
                    ideal_temp_max=30.0,
                    ideal_ph_min=6.0,
                    ideal_ph_max=6.8,
                    avg_yield_per_acre=150.0,
                    description="Tomato is one of the most important protective food crops in India.",
                    image_url="/media/crops/tomato.jpg"
                )
            ]
            db.add_all(crops)
            await db.flush()

        # 2. Seed default user & profile
        user_result = await db.execute(select(User).where(User.email == "farmer@rootgs.demo"))
        if not user_result.scalar_one_or_none():
            print("👨‍🌾 Seeding demo farmer user...")
            demo_farmer = User(
                email="farmer@rootgs.demo",
                phone="9876543210",
                hashed_password=hash_password("demo1234"),
                full_name="Rajasekar Krishnan",
                role=UserRole.farmer,
                is_active=True,
                is_verified=True,
                preferred_language="en"
            )
            db.add(demo_farmer)
            await db.flush()

            profile = FarmerProfile(
                user_id=demo_farmer.id,
                district="Coimbatore",
                state="Tamil Nadu",
                total_land_acres=4.5,
                farming_experience_years=12,
                bio="Growing organic vegetables and paddy in Western Tamil Nadu."
            )
            db.add(profile)
            await db.flush()

            # Add a default farm
            farm = Farm(
                owner_id=demo_farmer.id,
                name="Kongu Agro Farm",
                latitude=11.0168,
                longitude=76.9558,
                total_area_acres=4.5,
                soil_type=SoilType.loamy,
                irrigation_type=IrrigationType.drip,
                health_score=85.0
            )
            db.add(farm)
            await db.flush()

        # 3. Seed government schemes
        scheme_result = await db.execute(select(GovernmentScheme))
        if not scheme_result.scalars().first():
            print("🏛️ Seeding government agriculture schemes...")
            schemes = [
                GovernmentScheme(
                    name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                    authority="Central Government",
                    category="income_support",
                    description="An initiative by the government of India in which all farmers get up to ₹6,000 per year in three installments as minimum income support.",
                    benefits="₹6,000 per year direct benefit transfer",
                    eligibility="Small and marginal farmer families with combined landholding up to 2 hectares",
                    required_documents="Aadhaar Card, Land Records, Bank Account Details",
                    max_benefit_amount=6000.0,
                    is_active=True
                ),
                GovernmentScheme(
                    name="Pradhan Mantri Fasal Bima Yojana (PM-FBY)",
                    authority="Central Government",
                    category="crop_insurance",
                    description="An government sponsored crop insurance scheme that integrates multiple stakeholders to protect farmers against losses from natural calamities.",
                    benefits="Comprehensive risk cover from pre-sowing to post-harvest losses due to non-preventable risks.",
                    eligibility="All farmers growing notified crops in notified areas including tenant farmers.",
                    required_documents="Aadhaar Card, Land Records, Sowing Certificate",
                    is_active=True
                )
            ]
            db.add_all(schemes)
            await db.flush()

        # 4. Seed market prices
        price_result = await db.execute(select(MarketPrice))
        if not price_result.scalars().first():
            print("📈 Seeding market price listings...")
            prices = [
                MarketPrice(
                    crop_name="Rice (Paddy)",
                    market_name="Coimbatore Mandi",
                    state="Tamil Nadu",
                    district="Coimbatore",
                    price_date=datetime.date.today(),
                    min_price=2100.0,
                    max_price=2500.0,
                    modal_price=2300.0,
                    unit="quintal"
                ),
                MarketPrice(
                    crop_name="Tomato",
                    market_name="Coimbatore Mandi",
                    state="Tamil Nadu",
                    district="Coimbatore",
                    price_date=datetime.date.today(),
                    min_price=1500.0,
                    max_price=2200.0,
                    modal_price=1800.0,
                    unit="quintal"
                )
            ]
            db.add_all(prices)
            await db.flush()

        await db.commit()
    print("✨ Seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
