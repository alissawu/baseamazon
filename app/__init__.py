from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB

# Import all blueprints
from app.index import bp as index_bp
from app.users import bp as user_bp
from app.wishlist import bp as wishlist_bp
from app.feedback import bp as feedback_bp
from app.product import bp as product_bp
from app.purchase import bp as purchase_bp
from app.sellers import bp as sellers_bp
from app.cart import bp as cart_bp  # Import cart blueprint

app = Flask(__name__)

# Set up login manager
login = LoginManager()
login.login_view = 'users.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database and login manager
    app.db = DB(app)
    login.init_app(app)

    # Register blueprints
    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(sellers_bp)
    app.register_blueprint(cart_bp)  # Register the cart blueprint

    return app
