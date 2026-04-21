from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_username: str
    database_password: str
    database_name: str
    secret_key: str
    algorithm: str = "HS256"
    redis_url: str = "redis://localhost:6379/0"
    football_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()  # type: ignore