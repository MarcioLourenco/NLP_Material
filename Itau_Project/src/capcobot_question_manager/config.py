"""Config settings for for development, testing and production environments."""
import os
import sys
from pathlib import Path

HERE = Path(__file__).parent

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

path_root = Path(__file__).parents[0]
sys.path.append(str(path_root))


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "open sesame")
    AWS_SECRET_ACCESS_KEY = os.environ["aws_secret_access_key"]
    AWS_ACCESS_KEY_ID = os.environ["aws_access_key_id"]
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRE_HOURS = 0
    TOKEN_EXPIRE_MINUTES = 0
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SWAGGER_UI_DOC_EXPANSION = "list"
    RESTX_MASK_SWAGGER = False
    JSON_SORT_KEYS = False
    DEBUG = False
    BUCKET = os.getenv("BUCKET", "poc-vanilla")
    DATA_FOLDER = "data"
    SITE_NAME = "https://d13tzgfoyi2luj.cloudfront.net"
    FILES_FORMAT = ["pdf"]
    STORAGE = os.getenv("STORAGE", "S3")


class TestingConfig(Config):
    """Testing configuration."""

    ENVIRONMENT = "testing"
    TESTING = True
    BUCKET = "test_bucket"
    WORKDIR = "test/"
    # SQLALCHEMY_DATABASE_URI = SQLITE_TEST


class DevelopmentConfig(Config):
    """Development configuration."""

    ENVIRONMENT = "development"
    TOKEN_EXPIRE_MINUTES = 15
    DEBUG = True
    WORKDIR = "development/"
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", SQLITE_DEV)


class ProductionConfig(Config):
    """Production configuration."""

    ENVIRONMENT = "production"
    TOKEN_EXPIRE_HOURS = 1
    BCRYPT_LOG_ROUNDS = 13
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", SQLITE_PROD)
    PRESERVE_CONTEXT_ON_EXCEPTION = True
    WORKDIR = "production/"


ENV_CONFIG_DICT = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
)


def get_config(config_name=""):
    """Retrieve environment configuration settings."""
    if config_name:
        os.environ["CAPCOBOT_ENV"] = config_name

    if "CAPCOBOT_ENV" in os.environ:
        return ENV_CONFIG_DICT.get(os.environ["CAPCOBOT_ENV"])

    os.environ["CAPCOBOT_ENV"] = "development"
    return ENV_CONFIG_DICT.get(os.environ["CAPCOBOT_ENV"])
