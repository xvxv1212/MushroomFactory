from pathlib import Path
from pydantic.v1 import BaseSettings
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import text
from model import Admin, AiEvaluation, ChatRoom, Chatting, LlmRole, Score

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = PROJECT_ROOT / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
engine_url = create_engine(settings.DATABASE_URL, echo=True, pool_pre_ping=True)


def conn():
    # 기존 테이블은 유지하고, 없는 테이블만 생성합니다.
    # 이번 패치의 ai_evaluation 테이블도 여기서 최초 1회 자동 생성됩니다.
    SQLModel.metadata.create_all(bind=engine_url)


def get_session():
    with Session(engine_url) as session:
        yield session


def database_is_available() -> bool:
    """DB 장애 여부를 빠르게 확인. 실패를 밖으로 전파하지 않습니다."""
    try:
        with engine_url.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
