from pydantic_settings import BaseSettings, SettingsConfigDict


class ServicesSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_file=".env")

    DATABASE_URL: str
    SECRET_KEY: str


config = ServicesSettings()
