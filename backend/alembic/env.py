from sqlalchemy import create_engine

from alembic import context
from app.adapters.output.modelos import Base
from app.infrastructure.configuracion import Configuracion

metadatos_destino = Base.metadata
url = Configuracion().url_base_datos
if context.is_offline_mode():
    context.configure(url=url, target_metadata=metadatos_destino, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with create_engine(url).connect() as conexion:
        context.configure(connection=conexion, target_metadata=metadatos_destino)
        with context.begin_transaction():
            context.run_migrations()
