from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import current_user
from humanize import naturaltime
from .models.sellers import Seller
from .models.product import Product

bp = Blueprint('sellers', __name__)

@bp.route('/sellers', methods=['GET'])
def get_seller_products():
    acct_ID = request.args.get('acct_ID')
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    if acct_ID:
        try:
            acct_ID = int(acct_ID.strip())
        except ValueError:
            return "Invalid Account ID"
        products = Seller.get_products_by_seller_id(acct_ID)
        return render_template('sellers.html', products=products)
    else:
        sellers = Seller.get_all_sellers()
        return render_template('sellers.html', sellers=sellers)
