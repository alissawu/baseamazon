from flask import render_template, redirect, url_for, abort, request, current_app as app
from flask_login import current_user
from decimal import Decimal
# from .cart import Cart
from .models.order import Order
from flask import Blueprint

bp = Blueprint('carts', __name__)

@bp.route('/cart/<int:uid>')
def cart(uid):
    cart_items = app.db.execute('''
        SELECT ci.cart_item_ID, p.name, p.price, ci.quantity, ci.item_price
        FROM CartItem ci
        JOIN Products p ON ci.product_ID = p.product_ID
        WHERE ci.cart_ID = (SELECT cart_ID FROM Cart WHERE acct_ID = :uid)
    ''', uid=uid)
    return render_template('cart.html', cart_items=cart_items, uid=uid)

@bp.route('/update_quantities', methods=['POST'])
def update_quantities():
    for key in request.form:
        if key.startswith('quantity_'):
            cart_item_id = key.split('_')[1]
            new_quantity = int(request.form[key])
            app.db.execute('''
                UPDATE CartItem
                SET quantity = :new_quantity
                WHERE cart_item_ID = :cart_item_id
            ''', new_quantity=new_quantity, cart_item_id=cart_item_id)
    
    return redirect(url_for('carts.cart', uid=current_user.id))

@bp.route('/remove_item/<int:cart_item_id>', methods=['POST'])
def remove_item(cart_item_id):
    app.db.execute('''
        DELETE FROM CartItem
        WHERE cart_item_ID = :cart_item_id
    ''', cart_item_id=cart_item_id)
    
    return redirect(url_for('carts.cart', uid=current_user.id))

@bp.route('/submit_cart', methods=['POST'])
def submit_cart():
    user_id = current_user.id
    cart_items = app.db.execute('''
        SELECT ci.cart_item_ID, ci.product_ID, ci.seller_ID, ci.quantity, ci.item_price
        FROM CartItem ci
        WHERE ci.cart_ID = (SELECT cart_ID FROM Cart WHERE acct_ID = :user_id)
    ''', user_id=user_id)

    total_cost = sum(Decimal(item['item_price']) * item['quantity'] for item in cart_items)
    current_balance = app.db.execute('''
        SELECT balance FROM Users WHERE id = :user_id
    ''', user_id=user_id)[0]['balance']

    if total_cost > current_balance:
        abort(400, "Insufficient balance to complete the order.")

    app.db.execute('''
        UPDATE Users SET balance = balance - :total_cost WHERE id = :user_id
    ''', total_cost=total_cost, user_id=user_id)

    order_id = app.db.execute('''
        INSERT INTO Orders (acct_ID, total_cost) 
        VALUES (:user_id, :total_cost)
        RETURNING order_ID
    ''', user_id=user_id, total_cost=total_cost)[0]['order_ID']

    for item in cart_items:
        app.db.execute('''
            INSERT INTO OrderItem (order_ID, product_ID, seller_ID, quantity, item_price)
            VALUES (:order_id, :product_id, :seller_id, :quantity, :item_price)
        ''', order_id=order_id, product_id=item['product_ID'], seller_id=item['seller_ID'], 
            quantity=item['quantity'], item_price=item['item_price'])

    app.db.execute('''
        DELETE FROM CartItem WHERE cart_ID = (SELECT cart_ID FROM Cart WHERE acct_ID = :user_id)
    ''', user_id=user_id)

    return redirect(url_for('carts.cart', uid=user_id))

@bp.route('/orders/<int:uid>')
def orders(uid):
    if current_user.id != uid:
        return redirect(url_for('users.login'))

    orders = app.db.execute('''
        SELECT o.order_ID, o.total_cost, o.order_date, o.order_status
        FROM Orders o
        WHERE o.acct_ID = :uid
    ''', uid=uid)

    return render_template('orders.html', orders=orders)

@bp.route('/order_details/<int:uid>/<int:order_id>')
def order_details(uid, order_id):
    if current_user.id != uid:
        return redirect(url_for('users.login'))

    order_items = app.db.execute('''
        SELECT oi.product_ID, p.name, oi.quantity, oi.item_price, oi.order_item_status
        FROM OrderItem oi
        JOIN Products p ON oi.product_ID = p.product_ID
        WHERE oi.order_ID = :order_id
    ''', order_id=order_id)

    return render_template('order_details.html', order_items=order_items)