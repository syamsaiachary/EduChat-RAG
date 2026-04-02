import asyncio
from app.db.postgres import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings
from app.core.logger import logger

async def seed_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin:
            logger.info(f"Creating default admin user: {settings.ADMIN_EMAIL}")
            admin_user = User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            logger.info("Admin user created successfully.")
        else:
            logger.info("Admin user already exists.")
    except Exception as e:
        logger.error(f"Error seeding admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_admin())
