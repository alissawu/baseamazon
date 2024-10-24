from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user
from flask import Blueprint
from flask import current_app as app

bp = Blueprint('products', __name__)

PER_PAGE = 10

# List all products with filtering, sorting, and pagination
@bp.route('/get_products', methods=['GET', 'POST'])
def get_products():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE
    selected_category = request.args.get('category', 'all')
    search_keywords = request.args.get('keywords', '')

    # Count total products
    count_query = '''
        SELECT COUNT(*)
        FROM Products
        WHERE (name ILIKE :keywords OR description ILIKE :keywords)
    '''
    total_result = app.db.execute(count_query, keywords=f'%{search_keywords}%')
    total = total_result[0][0] if total_result else 0

    # Fetch products with filtering, sorting, and pagination
    product_query = '''
        SELECT p.product_ID, p.name, p.price, p.description, p.category, p.image,
               (SELECT AVG(urp.rating_num) FROM UserReviewsProduct urp WHERE urp.product_ID = p.product_ID) AS avg_rating
        FROM Products p
        WHERE (p.name ILIKE :keywords OR p.description ILIKE :keywords)
        ORDER BY p.name ASC
        LIMIT :limit OFFSET :offset
    '''
    products = app.db.execute(product_query, keywords=f'%{search_keywords}%', limit=PER_PAGE, offset=offset)

    return render_template('products.html', 
                           products=products,
                           total=total,
                           page=page,
                           per_page=PER_PAGE,
                           search_keywords=search_keywords,
                           selected_category=selected_category)

# View detailed product page
@bp.route('/product_details/<int:pid>', methods=['GET', 'POST'])
def product_details(pid):
    # Fetch product details
    product_query = '''
        SELECT p.product_ID, p.name, p.price, p.description, p.category, p.image,
               (SELECT AVG(urp.rating_num) FROM UserReviewsProduct urp WHERE urp.product_ID = p.product_ID) AS avg_rating,
               (SELECT COUNT(urp.rating_num) FROM UserReviewsProduct urp WHERE urp.product_ID = p.product_ID) AS review_count
        FROM Products p
        WHERE p.product_ID = :pid
    '''
    product = app.db.execute(product_query, pid=pid)

    # Fetch reviews for the product
    review_query = '''
        SELECT urp.customer_ID, urp.rating_message, urp.rating_num, urp.review_date, u.firstname, u.lastname
        FROM UserReviewsProduct urp
        JOIN Users u ON u.acct_ID = urp.customer_ID
        WHERE urp.product_ID = :pid
        ORDER BY urp.review_date DESC
    '''
    reviews = app.db.execute(review_query, pid=pid)

    return render_template('detailed_product.html', 
                           product=product[0], 
                           reviews=reviews)

# Add product to cart
@bp.route('/add_to_cart/<int:pid>', methods=['POST'])
def add_to_cart(pid):
    if not current_user.is_authenticated:
        flash("Please log in to add products to your cart", "warning")
        return redirect(url_for('auth.login'))

    uid = current_user.id
    seller_id = request.form.get('seller_id')
    quantity = int(request.form.get('quantity'))

    if not seller_id or not quantity:
        flash("Invalid seller or quantity selected", "danger")
        return redirect(url_for('products.product_details', pid=pid))

    # Check available quantity
    available_quantity = get_seller_quantity(seller_id, pid)
    if quantity > available_quantity:
        flash("Requested quantity exceeds available stock", "danger")
        return redirect(url_for('products.product_details', pid=pid))

    # Get the user's cart ID
    cart_id = get_cart_id(uid)

    # Add to cart or update if the product is already in the cart
    cart_query = '''
        INSERT INTO CartItem (cart_ID, product_ID, seller_ID, quantity, item_price)
        VALUES (:cart_id, :product_id, :seller_id, :quantity, 
                (SELECT price FROM Products WHERE product_ID = :product_id))
        ON CONFLICT (cart_ID, product_ID, seller_ID) DO UPDATE
        SET quantity = CartItem.quantity + :quantity
    '''
    app.db.execute(cart_query, cart_id=cart_id, product_id=pid, seller_id=seller_id, quantity=quantity)

    flash("Product added to cart", "success")
    return redirect(url_for('products.product_details', pid=pid))

# Add a review to a product
@bp.route('/add_review/<int:pid>', methods=['POST'])
def add_review(pid):
    if not current_user.is_authenticated:
        flash("Please log in to leave a review", "warning")
        return redirect(url_for('auth.login'))

    uid = current_user.id
    rating_num = int(request.form.get('rating_num'))
    rating_message = request.form.get('rating_message')

    # Validate rating and review content
    if not (1 <= rating_num <= 5):
        flash("Rating must be between 1 and 5", "danger")
        return redirect(url_for('products.product_details', pid=pid))

    review_query = '''
        INSERT INTO UserReviewsProduct (customer_ID, product_ID, rating_num, rating_message, review_date)
        VALUES (:customer_id, :product_id, :rating_num, :rating_message, current_timestamp)
        ON CONFLICT (customer_ID, product_ID) DO UPDATE
        SET rating_num = EXCLUDED.rating_num, rating_message = EXCLUDED.rating_message
    '''
    app.db.execute(review_query, customer_id=uid, product_id=pid, rating_num=rating_num, rating_message=rating_message)

    flash("Review submitted successfully", "success")
    return redirect(url_for('products.product_details', pid=pid))

# Helper function to get the available quantity of a product for a seller
def get_seller_quantity(seller_id, product_id):
    query = '''
        SELECT available_quantity
        FROM Inventory
        WHERE seller_ID = :seller_id AND product_ID = :product_id
    '''
    result = app.db.execute(query, seller_id=seller_id, product_id=product_id)
    return result[0][0] if result else 0

# Helper function to get or create the user's cart ID
def get_cart_id(uid):
    cart_query = '''
        SELECT cart_ID FROM Cart WHERE acct_ID = :uid
    '''
    result = app.db.execute(cart_query, uid=uid)
    
    if not result:
        insert_cart_query = '''
            INSERT INTO Cart (acct_ID, total_cost) VALUES (:uid, 0) RETURNING cart_ID
        '''
        result = app.db.execute(insert_cart_query, uid=uid)

    return result[0][0]
