from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from src.db import Base
from src.db.models import *
from src.core.config import load_config
from src.db import Db

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_online() -> None:
    # Use our application's configuration logic to initialize the engine
    mycel_config = load_config("config.json")
    url = mycel_config.sqlalchemy_url

    connectable = Db(url).engine  # Or create_engine(url) if we change Db to take a URL

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()



run_migrations_online()
