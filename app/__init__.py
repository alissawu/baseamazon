from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB
from app.wishlist import bp as wishlist_bp



login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    

    app.db = DB(app)
    login.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .wishlist import bp as wishlist_bp
    app.register_blueprint(wishlist_bp)

    from .feedback import bp as feedback_bp
    app.register_blueprint(feedback_bp)

    from .product import bp as product_bp
    app.register_blueprint(product_bp)

    return app
