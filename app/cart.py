from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from flask_login import current_user
from flask import current_app as app
from app.models.cart import Cart
from app.models.purchase import Purchase
from datetime import datetime
from humanize import naturaltime
import uuid
from collections import Counter


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
        cart_items = Cart.get_all_by_uid(current_user.id)
        if not cart_items:
            flash("Your cart is empty.")
            return redirect(url_for('cart.cart'))

        # Count how many of each product is being purchased
        product_counts = Counter([item.pid for item in cart_items])

        # Calculate total cost
        total_cost = sum(item.product_price for item in cart_items)

        # Check user funds first
        if total_cost > current_user.account_balance:
            flash("Insufficient funds. Please remove some items or add more funds.")
            return redirect(url_for('cart.cart'))

        # Check stock for each distinct product before finalizing
        product_data = []
        for pid, count in product_counts.items():
            product = app.db.execute('''
                SELECT Products.id, Products.price, Products.available, Seller.quantity
                FROM Products
                JOIN Seller ON Seller.product_ID = Products.id
                WHERE Products.id = :product_id
            ''', product_id=pid)

            if not product:
                flash("A product in your cart no longer exists.")
                return redirect(url_for('cart.cart'))

            pid_db, price, available, quantity = product[0]

            # Check if product is available and has enough quantity
            if not available or quantity < count:
                flash(f"Not enough stock for product ID {pid_db}. Requested: {count}, Available: {quantity}")
                return redirect(url_for('cart.cart'))

            new_quantity = quantity - count
            product_data.append((pid_db, new_quantity))

        # If we reach here, all items have enough stock
        # Deduct total cost from user first
        current_user.deduct(total_cost)

        # Update inventory and availability for each product
        for (pid_db, new_quantity) in product_data:
            if new_quantity == 0:
                app.db.execute('''
                    UPDATE Seller SET quantity = 0 WHERE product_ID = :product_id
                ''', product_id=pid_db)
                app.db.execute('''
                    UPDATE Products SET available = False WHERE id = :product_id
                ''', product_id=pid_db)
            else:
                app.db.execute('''
                    UPDATE Seller SET quantity = :quantity WHERE product_ID = :product_id
                ''', quantity=new_quantity, product_id=pid_db)

        # Proceed with checkout and add all items to Purchases
        order_id = str(uuid.uuid4())
        # Add each cart item as a purchase record
        for item in cart_items:
            Purchase.add(current_user.id, order_id, item.pid)

        # Clear user's cart
        Cart.clear(current_user.id)

        flash("Checkout successful!")
        return redirect(url_for('purchase.purchase'))
    else:
        return redirect(url_for('users.login'))
    
@bp.route('/cart/user', methods=['GET'])
def cart_user():
    user_id = request.args.get('acct_ID', type=int)

    if user_id is None:
        flash("User ID is required.")
        return redirect(url_for('index.index'))

    # Fetch the cart items for the given user ID
    items = Cart.get_all_by_uid(user_id)

    # Render the cart.html template even if the cart is empty
    return render_template('cart.html', items=items, humanize_time=humanize_time)



@bp.app_template_filter('humanize_time')
def humanize_time(dt):
    return naturaltime(datetime.now() - dt)
