import os

from flask import Flask, render_template
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException
from app.models import Diagnosis, ModelType, Feature

# instantiate extensions
login_manager = LoginManager()


def create_app(environment="development"):

    from config import config
    from .views import main_blueprint
    from .auth.views import auth_blueprint
    from .demo.views import demo_blueprint
    from .auth.models import User, AnonymousUser
    from .database import db

    # Instantiate app.
    app = Flask(__name__)

    # Set app config.
    env = os.environ.get("FLASK_ENV", environment)
    app.config.from_object(config[env])
    config[env].configure(app)

    # Set up extensions.
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints.
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(demo_blueprint, url_prefix="/demo")

    # Set up flask login.
    @login_manager.user_loader
    def get_user(id):
        return User.query.get(int(id))

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    login_manager.anonymous_user = AnonymousUser

    # Error handlers.
    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        return render_template("error.html", error=exc), exc.code

    return app


def fill_db():
    ModelType(name='XGBoost').save()
    Diagnosis(name='Cancer').save()
    Diagnosis(name='Cardiac').save()
    Diagnosis(name='Dermatology').save()
    Diagnosis(name='Diabetic').save()
    Feature(name='Age', short_name='age').save()
    Feature(name='Num. of Pregnacies', short_name='preg').save()
