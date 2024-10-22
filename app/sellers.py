from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from humanize import naturaltime
from app.models.purchase import Purchase  # Changed from PurchaseItem to Purchase
from datetime import datetime

bp = Blueprint('sellers', __name__)

@bp.route('/sellers')
def sellers_inventory():
    return render_template('sellers.html')

class Seller:
    def __init__(self, acct_id, product_id, product_name):
        self.acct_id = acct_id
        self.product_id = product_id
        self.product_name = product_name

    @staticmethod
    def get(acct_id):
        rows = app.db.execute('''
        SELECT Sellers.acct_id, Sellers.product_id, Products.id, Products.name
        FROM Sellers
        JOIN Products ON Sellers.product_id = Products.id
        ''', acct_id=acct_id)
        return [Seller(*row) for row in rows]