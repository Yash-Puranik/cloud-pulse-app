import os


class Settings:
    """Reads environment variables with production-safe defaults."""
    APP_NAME: str = os.getenv("APP_NAME", "cloud-pulse")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_PORT: int = int(os.getenv("APP_PORT", "8080"))
    AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


settings = Settings()