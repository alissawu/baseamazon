from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from app.models.product import Product
from flask import current_app as app

bp = Blueprint('sellers', __name__)

@bp.route('/sellers', methods=['GET', 'POST'])
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
    def get_products_by_seller_id(seller_id):
        rows = app.db.execute('''
        SELECT Products.id, Products.name, Products.price, Products.available
        FROM Seller
        JOIN Products ON Seller.product_id = Products.id
        WHERE Seller.acct_id = :acct_id
        ''', acct_id=seller_id)
        
        return [Product(*row) for row in rows] if rows else []
