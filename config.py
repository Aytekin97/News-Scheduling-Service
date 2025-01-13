from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    db_url: str
    aggregator_api_url: str
    
    def __init__(self, **data):
        super().__init__(**data)
        # Parse DB_URL as a list if it's a comma-separated string
        if isinstance(self.db_url, str):
            self.db_url = [url.strip() for url in self.db_url.split(",")]


def load_settings():
    try:
        return Settings()
    except ValidationError as e:
        exit(str(e))


settings = load_settings()
