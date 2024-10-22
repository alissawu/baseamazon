from flask import Blueprint, render_template, redirect, url_for
from flask import current_app as app
from flask_login import current_user
from humanize import naturaltime
from app.models.purchase import Purchase  # Changed from PurchaseItem to Purchase
from datetime import datetime

bp = Blueprint('sellers', __name__)

@bp.route('/sellers/<int:acct_id>')
def sellers_inventory(acct_id):
    products = Seller.get_products_by_seller(acct_id)
    sellers = Seller.get(acct_id)
    return render_template('sellers.html', sellers=sellers)

class Seller:
    def __init__(self, acct_id, product_id, name):
        self.acct_id = acct_id
        self.product_id = product_id
        self.name = name

    @staticmethod
    def get(acct_id):
        rows = app.db.execute('''
        SELECT acct_id, product_id
        FROM Sellers
        WHERE acct_id = :acct_id
        ''',
                              acct_id=acct_id)
        return Product(*(rows[0])) if rows is not None else None
    
    @staticmethod
    def get_all(acct_id):
        rows = app.db.execute('''
        SELECT Sellers.acct_id, Sellers.product_id, Products.name
        FROM Sellers
        JOIN Products ON Sellers.product_id = Products.id
        WHERE Sellers.acct_id = :acct_id
        ''', acct_id=acct_id)

        return [Product(*row) for row in rows]