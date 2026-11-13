from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "cargohub"
    DB_USER: str = "postgres"
    DB_PASSWORD: str

    APP_NAME: str = "CargoHub API"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_KEY: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
