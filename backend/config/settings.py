import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    mongo_url: str = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name: str = os.environ.get('DB_NAME', 'islamic_institute')
    
    # Security
    jwt_secret: str = os.environ.get('JWT_SECRET', 'islamic-institute-secret-key-2025-secure')
    jwt_algorithm: str = "HS256"
    access_token_expire_hours: int = 24
    
    # App
    app_name: str = "Islamic Institute Course Platform API"
    debug: bool = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # CORS
    cors_origins: list = ["*"]
    
    # Payment (SSLCommerz)
    sslcommerz_store_id: str = os.environ.get('SSLCOMMERZ_STORE_ID', '')
    sslcommerz_store_password: str = os.environ.get('SSLCOMMERZ_STORE_PASSWORD', '')
    sslcommerz_is_sandbox: bool = os.environ.get('SSLCOMMERZ_SANDBOX', 'True').lower() == 'true'
    
    class Config:
        env_file = ".env"

settings = Settings()