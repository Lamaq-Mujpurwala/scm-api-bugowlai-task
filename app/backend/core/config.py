from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Manages application settings loaded from environment variables.
    Utilizes Pydantic for validation and type hints.
    """
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
