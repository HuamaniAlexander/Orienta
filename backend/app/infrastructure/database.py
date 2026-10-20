from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.settings import Settings


def session_factory(settings: Settings):
    engine = create_engine(
        settings.database_url, pool_pre_ping=True, connect_args={"connect_timeout": 5}
    )
    return sessionmaker(engine, expire_on_commit=False)
