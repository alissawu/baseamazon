from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from flask_login import current_user
from app.models.cart import Cart
from app.models.purchase import Purchase
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

@bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    if current_user.is_authenticated:
        Cart.remove(current_user.id, product_id)
        return redirect(url_for('cart.cart'))
    else:
        return redirect(url_for('users.login'))

@bp.route('/cart/checkout', methods=['POST'])
def checkout():
    if current_user.is_authenticated:
        # Get all cart items for the current user
        cart_items = Cart.get_all_by_uid(current_user.id)
        if not cart_items:
            flash("Your cart is empty.")
            return redirect(url_for('cart.cart'))

        # Calculate total cost of items in the cart
        total_cost = sum(item.product_price for item in cart_items)

        # Check if the user has enough balance
        if total_cost > current_user.account_balance:
            flash("Insufficient funds. Please remove some items or add more funds.")
            return redirect(url_for('cart.cart'))

        # Proceed with checkout
        for item in cart_items:
            # Add item to purchases
            Purchase.add(current_user.id, item.pid)

        # Deduct total cost from user's balance
        current_user.deduct(total_cost)

        # Clear user's cart
        Cart.clear(current_user.id)

        flash("Checkout successful!")
        return redirect(url_for('purchase.purchase'))
    else:
        return redirect(url_for('users.login'))

@bp.app_template_filter('humanize_time')
def humanize_time(dt):
    return naturaltime(datetime.now() - dt)
