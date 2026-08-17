"""Seed database with sample data."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.models.base import engine, async_session, init_db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.project import Project
from app.core.security import hash_password


async def seed():
    """Seed the database with sample data."""
    await init_db()

    async with async_session() as session:
        # Create sample tenant
        tenant = Tenant(
            name="Sunrise Infra Developers",
            slug="sunrise-infra",
            plan="pro",
        )
        session.add(tenant)
        await session.flush()

        # Create admin user
        admin = User(
            tenant_id=tenant.id,
            email="admin@sunrise.com",
            hashed_password=hash_password("admin123"),
            full_name="Admin User",
            role="admin",
        )
        session.add(admin)

        # Create sample project
        project = Project(
            tenant_id=tenant.id,
            name="Sunrise Residency",
            slug="sunrise-residency",
            builder_name="Sunrise Infra Developers",
            location="Sector 87, Gurugram, Haryana",
            rera_number="HRERA-UP-RERA-2027-00421 (dummy)",
            configurations={
                "2 BHK": {"size": "850 - 1050 sq.ft.", "price_range": "Rs 65 lakh - Rs 78 lakh"},
                "3 BHK": {"size": "1250 - 1500 sq.ft.", "price_range": "Rs 95 lakh - Rs 1.15 crore"},
                "4 BHK": {"size": "1750 - 2100 sq.ft.", "price_range": "Rs 1.6 crore - Rs 1.9 crore"},
            },
            amenities=[
                "Clubhouse with gym and indoor games",
                "Swimming pool",
                "Landscaped gardens and jogging track",
                "Kids play area",
                "24x7 security with CCTV",
                "Power backup and EV charging points",
                "Covered parking",
            ],
            location_advantages=[
                "5 minutes from Dwarka Expressway",
                "20 minutes from Indira Gandhi International Airport",
                "15 minutes from IT parks / Cyber City",
                "Close to upcoming metro corridor",
                "Reputed schools and hospitals within 10 minutes",
            ],
            possession={
                "Phase 1 (Towers A, B, C)": "December 2027",
                "Phase 2 (Towers D, E + retail)": "Mid 2028",
            },
            payment_plan="20% booking amount, balance on construction milestones or bank loan.",
            agent_name="Priya",
            language_mode="auto",
        )
        session.add(project)

        await session.commit()

        print("✓ Database seeded successfully!")
        print(f"  Tenant: {tenant.name} (slug: {tenant.slug})")
        print(f"  Admin: {admin.email} (password: admin123)")
        print(f"  Project: {project.name}")


if __name__ == "__main__":
    asyncio.run(seed())
