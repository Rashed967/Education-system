import motor.motor_asyncio
from ..config.settings import settings

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url)
database = client[settings.db_name]

async def get_database():
    """Get database instance"""
    return database