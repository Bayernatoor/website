import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from config import Config
from elasticsearch import Elasticsearch
from redis import Redis
import rq


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():

        db.init_app(app)
        migrate.init_app(app, db)
        login.init_app(app)
        mail.init_app(app)
        bootstrap.init_app(app)
        moment.init_app(app)
        babel.init_app(app)
        app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
            if app.config['ELASTICSEARCH_URL'] else None
        app.redis = Redis.from_url(app.config['REDIS_URL'])
        app.task_queue = rq.Queue('website-tasks', connection=app.redis)

        from app.errors import bp as errors_bp
        app.register_blueprint(errors_bp)

        from app.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')

        from app.main import bp as main_bp
        app.register_blueprint(main_bp)

        from app.api import bp as api_bp
        app.register_blueprint(api_bp, url_prefix='/api')

        if not app.debug and not app.testing:
            if current_app.config['MAIL_SERVER']:
                auth = None
                if current_app.config['MAIL_USERNAME'] or current_app.config['MAIL_PASSWORD']:
                    auth = (current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
                secure = None
                if current_app.config['MAIL_USE_TLS']:
                    secure = ()
                mail_handler = SMTPHandler(
                    mailhost=(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']),
                    fromaddr='no-reply@' + current_app.config['MAIL_SERVER'],
                    toaddrs=current_app.config['ADMINS'], subject='Website Failure',
                    credentials=auth, secure=secure)
                mail_handler.setLevel(logging.ERROR)
                app.logger.addHandler(mail_handler)

            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/website.log', maxBytes=10248,
                                               backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(messsage)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Website startup')\

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models
