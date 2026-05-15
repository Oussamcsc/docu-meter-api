from logging.config import fileConfig

from alembic import context

from app.core.config import get_settings
from app.core.database import Base

# Import models for autogenerate metadata.
import app.api_keys.models  # noqa: F401
import app.organizations.models  # noqa: F401
import app.projects.models  # noqa: F401
import app.usage.models  # noqa: F401
import app.users.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine

    url = config.get_main_option("sqlalchemy.url")
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    connectable = create_engine(url, connect_args=connect_args)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
