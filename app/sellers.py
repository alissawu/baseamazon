from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import current_user
from humanize import naturaltime
from app.models.product import Product
from flask import current_app as app

bp = Blueprint('sellers', __name__)

# add authentication
@bp.route('/sellers')
def sellers():
    if current_user.is_authenticated:
        return render_template('sellers.html')
    else:
        return redirect(url_for('users.login'))

@bp.route('/sellers/<int:user_id>', methods=['POST'])
class Seller:
    def __init__(self, acct_id, product_id, product_name, price, available):
        self.acct_id = acct_id
        self.product_id = product_id
        self.product_name = product_name
        self.price = price
        self.available = available

    @staticmethod
    # query for products based on the seller id
    def get_products_by_seller_id(acct_id):
        rows = app.db.execute('''
        SELECT Seller.acct_id, Products.id, Products.name, Products.price, Products.available
        FROM Seller
        JOIN Products ON Seller.product_id = Products.id
        WHERE Seller.acct_id = :acct_id
        ''', acct_id=acct_id)

        # Convert rows into a list of dictionaries
        products = [Product(*row) for row in rows]
        
        return jsonify(products)

# implement search
@bp.route('/sellers/<int:acct_id>', methods=['GET'])
def get_seller_products(acct_id):
    products = Seller.get_products_by_seller_id(acct_id)
    return render_template('sellers.html', products=products)
