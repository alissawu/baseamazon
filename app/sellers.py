from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import current_user
from humanize import naturaltime
from app.models.product import Product
from flask import current_app as app

bp = Blueprint('sellers', __name__)

@bp.route('/sellers/<int:user_id>', methods=['GET'])
def sellers_inventory():
    products = []
    
    if request.method == 'POST':
        seller_id = request.form.get('seller_id')
        
        if seller_id:
            products = Product.get_products_by_seller_id(seller_id)
    
    return render_template('sellers.html', products=products)

class Seller:
    def __init__(self, acct_id, product_id):
        self.acct_id = acct_id
        self.product_id = product_id

    @staticmethod
    # query for products based on the seller id
    def get_products_by_seller_id(seller_id):
        rows = app.db.execute('''
        SELECT Products.id, Products.name, Products.price, Products.available
        FROM Seller
        JOIN Products ON Seller.product_id = Products.id
        WHERE Seller.acct_id = :acct_id
        ''', acct_id=seller_id)

        # Convert rows into a list of dictionaries
        product = [Product(*row) for row in rows]
        
        return jsonify(product)
