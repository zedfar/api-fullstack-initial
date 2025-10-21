# app/seed_data.py
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.role import Role

async def seed_roles():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Role))
        roles = result.scalars().all()

        if not roles:
            print("🌱 Seeding default roles...")
            default_roles = [
                {"name": "admin", "description": "Administrator - full access"},
                {"name": "user", "description": "Regular user - limited access"},
            ]

            for r in default_roles:
                session.add(Role(**r))
            await session.commit()
            print("✅ Default roles created.")
        else:
            print("✅ Roles already exist, skipping seeding.")


async def seed_all():
    await seed_roles()