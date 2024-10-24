from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import current_user
from humanize import naturaltime
from app.models.product import Product
from flask import current_app as app
from .models.sellers import Seller

from .models.product import Product

bp = Blueprint('sellers', __name__)

# add authentication
@bp.route('/sellers')
def sellers():
    if current_user.is_authenticated:
        return render_template('sellers.html')
    else:
        return redirect(url_for('users.login'))

# find all sellers
@bp.route('/sellers', methods=['GET'])
def sellers_inventory():
    sellers = Seller.get_all_sellers()
    return render_template('sellers.html', sellers=sellers)

# implement search
@bp.route('/sellers', methods=['GET'])
def get_seller_products():
    acct_ID = request.args.get('acct_ID')
    print(f"Received acct_ID: '{acct_ID}'")
    if acct_ID:
        try:
            acct_ID = int(acct_ID.strip())
        except ValueError:
            return "Invalid Account ID"
    else:
        return "Enter Valid Account ID"
    products = Seller.get_products_by_seller_id(acct_ID)
    # return products
    return render_template('sellers.html', products=products)
