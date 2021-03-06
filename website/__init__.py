from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv, environ, path
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv


db = SQLAlchemy()
DB_NAME = "database.db"
mail = Mail()


def create_app():
    mail = Mail()
    app = Flask(__name__)

    dotenv_path = path.join(path.dirname(__file__), ".env")
    load_dotenv(dotenv_path)

    app.debug = True

    app._static_folder = "static"
    app.config["SECRET_KEY"] = "helloworld"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    connect = f"mysql+pymysql://{getenv('DB_USERNAME')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}/{getenv('DB_NAME')}"
    app.config["SQLALCHEMY_DATABASE_URI"] = connect

    # toolbar = DebugToolbarExtension(app)
    # app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.config["MAIL_SERVER"] = "smtp.mailtrap.io"
    app.config["MAIL_PORT"] = 2525
    app.config["MAIL_USERNAME"] = "2bd40272ef58f7"
    app.config["MAIL_PASSWORD"] = "39d7d1dc080abe"
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False

    db.init_app(app)
    mail.init_app(app)

    Migrate(app, db, render_as_batch=True)

    from website.templates.views.views import views
    from website.auth import auth
    from website.templates.menu.menu import menu
    from website.templates.vehicles.vehicle import vehicle
    from website.templates.health.health import health
    from website.templates.mileage.mileage import mileage
    from website.templates.productivity.productivity import prod
    from website.templates.personal.personal import personal
    from website.templates.money.money import money

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(menu, url_prefix="/menu")
    app.register_blueprint(vehicle, url_prefix="/vehicle")
    app.register_blueprint(health, url_prefix="/health")
    app.register_blueprint(prod, url_prefix="/productivity")
    app.register_blueprint(personal, url_prefix="/personal")
    app.register_blueprint(mileage, url_prefix="/mileage")
    app.register_blueprint(money, url_prefix="/money")

    from website.models import User

    # create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    # if not path.exists("website/" + DB_NAME):
    db.create_all(app=app)
    print("Created database!")
