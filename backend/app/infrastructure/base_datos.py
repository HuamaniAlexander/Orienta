from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.configuracion import Configuracion


def crear_sesiones(configuracion: Configuracion):
    motor = create_engine(
        configuracion.url_base_datos, pool_pre_ping=True, connect_args={"connect_timeout": 5}
    )
    return sessionmaker(motor, expire_on_commit=False)
