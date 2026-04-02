from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    CHROMA_HOST: str
    CHROMA_PORT: int
    CHROMA_COLLECTION: str
    OLLAMA_BASE_URL: str
    EMBEDDING_MODEL: str
    GEMINI_API_KEY: str
    GEMINI_MODEL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_DAYS: int
    COOKIE_NAME: str
    ADMIN_EMAIL: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    CHAT_MEMORY_TURNS: int = 4
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
