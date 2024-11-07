import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the parent directory to Python path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.models import Base  # Import your models

# this is the Alembic Config object
config = context.config

# Set SQLAlchemy URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata  # Set metadata for migrations
