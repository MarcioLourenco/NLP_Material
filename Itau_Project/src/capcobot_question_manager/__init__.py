"""Flask app initialization via factory pattern."""
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from src.capcobot_question_manager.config import get_config

cors = CORS()
bcrypt = Bcrypt()


def create_app(config_name=""):
    application = Flask("api_capcobot_question_manager")
    application.config.from_object(get_config(config_name))
    from src.capcobot_question_manager.api import api_bp

    application.register_blueprint(api_bp)
    cors.init_app(application)
    bcrypt.init_app(application)

    return application
