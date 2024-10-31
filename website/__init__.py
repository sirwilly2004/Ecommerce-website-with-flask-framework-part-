from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta



db = SQLAlchemy()
DB_NAME = 'database.sqlite3'


def create_database():
    db.create_all()
    print('Database Created')


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '353HGDTD63839383'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Example: 16 MB limit
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)

 
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    from website.admin import admin
    from website.auth import auth
    from website.views import views
    from .models import Customer, Cart, Product, Order


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')


    # with app.app_context():
    #     create_database()

    return app


