from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import current_user
from humanize import naturaltime
from app.models.product import Product
from flask import current_app as app

from .models.product import Product

bp = Blueprint('sellers', __name__)

# add authentication
@bp.route('/sellers')
def sellers():
    if current_user.is_authenticated:
        return render_template('sellers.html')
    else:
        return redirect(url_for('users.login'))

@bp.route('/sellers/<int:acct_ID>', methods=['POST'])
class Seller:
    def __init__(self, acct_ID, product_ID, id, name, price, available):
        self.acct_ID = acct_ID
        self.product_ID = product_ID
        self.id = id
        self.name = name
        self.price = price
        self.available = available
    
    def get_all(available=True):
        rows = app.db.execute('''
        SELECT Seller.acct_ID, Products.id, Products.name, Products.price, Products.available
        FROM Seller
        JOIN Products ON Products.id = Seller.product_ID
        WHERE Products.available = :available
        ''',
                              available=available)
        return [Product(*row) for row in rows]

    # query for products based on the seller id
    def get_products_by_seller_id(acct_ID):
        rows = app.db.execute('''
        SELECT Seller.acct_ID, Products.id, Products.name, Products.price, Products.available
        FROM Seller
        JOIN Products ON Products.id = Seller.product_ID
        WHERE Seller.acct_ID = :acct_ID
        ''', acct_ID=acct_ID)

        return [Seller(*row) for row in rows]

    def get_all_sellers():
        rows = app.db.execute('''
        SELECT Sellers.acct_ID, Products.id, Products.name
        FROM Sellers
        JOIN Products ON Sellers.product_id = Products.id
        ''')

        return [Seller(*row) for row in rows]
 

# find all sellers
@bp.route('/sellers', methods=['GET'])
def sellers_inventory():
    sellers = Seller.get_all_sellers()
    return render_template('sellers.html', sellers=sellers)

# implement search
@bp.route('/sellers', methods=['GET'])
def get_seller_products():
    acct_ID = request.args.get('acct_id')
    products = Seller.get_products_by_seller_id(acct_ID)
    return render_template('sellers.html', products=products)
