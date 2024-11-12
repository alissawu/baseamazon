from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user
from app.models.cart import Cart
from datetime import datetime
from humanize import naturaltime

bp = Blueprint('cart', __name__)

@bp.route('/cart')
def cart():
    if current_user.is_authenticated:
        # Get all cart items for the current user
        items = Cart.get_all_by_uid(current_user.id)
        return render_template('cart.html', items=items, humanize_time=humanize_time)
    else:
        return redirect(url_for('users.login'))

@bp.route('/cart/add/<int:product_id>', methods=['POST'])
def cart_add(product_id):
    if current_user.is_authenticated:
        Cart.add(current_user.id, product_id)
        return redirect(url_for('cart.cart'))
    else:
        return redirect(url_for('users.login'))

@bp.app_template_filter('humanize_time')
def humanize_time(dt):
    return naturaltime(datetime.now() - dt)

@bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    if current_user.is_authenticated:
        Cart.remove(current_user.id, product_id)
        return redirect(url_for('cart.cart'))
    else:
        return redirect(url_for('users.login'))

@bp.route('/cart/user', methods=['GET'])
def get_cart_by_uid():
    if current_user.is_authenticated:
        # Get the user ID from the request
        uid = request.args.get('acct_ID')
        if uid is None:
            return jsonify({'error': 'User ID not provided'}), 400
        
        # Fetch all cart items by the specified user ID (uid)
        items = Cart.get_all_by_uid(uid)
        if not items:
            return jsonify({'error': 'No items found for this user.'}), 404
        return render_template('cart.html', items=items, humanize_time=humanize_time)
    else:
        return redirect(url_for('users.login'))