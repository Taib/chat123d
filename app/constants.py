from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    jwt_secret: str = "db358804fe6c48befd5308c1301a8526ba8827390075442b9d6e7e52e25137af"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour

    db_type: Literal["sql", "firebase", "mongo"] = "sql"
    pg_dsn: str = "mysql+pymysql://liboo_user:your_password_here@mariadb:3306/liboo"

    model_config = SettingsConfigDict(env_prefix="liboo_")

    max_overdue_loans: int = 20
    loan_duration_days: int = 14
    API_URL: str = "http://localhost:8000"
