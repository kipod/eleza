import os
from flask_wtf.csrf import CSRFProtect
from flask import Flask, render_template
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException

# instantiate extensions
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(environment="development"):
    from config import config
    from .main import main_blueprint
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
    csrf.init_app(app)

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
