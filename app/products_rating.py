from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
from flask import Blueprint
from app.models.product import Product  # Assuming Product model is defined in your app
from flask import jsonify

bp = Blueprint('product_rating', __name__)

# Constants for pagination and description length
PER_PAGE = 10
MAX_DESCRIPTION_LENGTH = 255

# Displays all reviews made by the current user
@bp.route('/product_rating')
def product_rating():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'review_date')
    order = request.args.get('order', 'desc')

    offset = (page - 1) * PER_PAGE

    reviews = app.db.execute(f'''
        SELECT urp.product_ID, urp.rating_message, urp.rating_num, urp.review_date, p.name 
        FROM UserReviewsProduct urp
        JOIN Products p ON p.id = urp.product_id

        WHERE urp.customer_ID = :uid
        ORDER BY {sort_by} {"DESC" if order == "desc" else "ASC"}
        LIMIT :limit OFFSET :offset
    ''', uid=current_user.id, limit=PER_PAGE, offset=offset)

    total_result = app.db.execute('SELECT COUNT(*) AS total_count FROM UserReviewsProduct WHERE customer_ID = :uid', uid=current_user.id)
    total = total_result[0][0] if total_result else 0

    return render_template('product_rating.html', reviews=reviews, total=total, page=page, per_page=PER_PAGE, sort_by=sort_by, order=order)

# Redirect to edit review page while keeping product ID
@bp.route('/redirect_to_edit_review', methods=['GET', 'POST'])
def redirect_to_edit_review():
    pid = request.args.get('pid')
    referring_page = request.referrer
    return redirect(url_for('product_rating.edit_review', pid=pid, referring_page=referring_page))

# Get current rating to view before updating
@bp.route('/edit_review/<int:pid>', methods=['GET', 'POST'])
def edit_review(pid):
    uid = current_user.id
    referring_page = request.args.get('referring_page')

    # Fetch review details for the current user and product
    ratings = app.db.execute('''
        SELECT rating_message, rating_num 
        FROM UserReviewsProduct 
        WHERE customer_ID = :uid AND product_ID = :pid
    ''', uid=uid, pid=pid)

    return render_template('edit_review.html', ratings=ratings[0], referring_page=referring_page)

# Updates the review for a product
@bp.route('/update_pr', methods=['POST'])
def update_data():
    # Get values for updating the review
    description = request.form.get('description')
    stars = request.form.get('stars')
    uid = current_user.id
    pid = request.form.get('pid')

    try:
        # Validate inputs
        if not pid:
            flash("Invalid product ID.", "danger")
            return redirect(url_for('product.detail', product_id=pid))

        if not (1 <= int(stars) <= 5):
            flash("Rating must be between 1 and 5.", "danger")
            return redirect(url_for('product.detail', product_id=pid))

        if len(description) > 255:
            flash("Description is too long.", "danger")
            return redirect(url_for('product.detail', product_id=pid))

        # Query for updating the review
        update_query = '''
            UPDATE UserReviewsProduct 
            SET rating_message = :description, rating_num = :stars 
            WHERE product_ID = :pid AND customer_ID = :uid
        '''
        app.db.execute(update_query, description=description, stars=stars, pid=pid, uid=uid)

        # Redirect back to the product page
        flash("Review updated successfully!", "success")
        return redirect(url_for('product.detail', product_id=pid))

    except Exception as e:
        flash(f"Error updating review: {e}", "danger")
        return redirect(url_for('product.detail', product_id=pid))

# Redirect to delete a review
@bp.route('/redirect_to_delete_review', methods=['GET', 'POST'])
def redirect_to_delete_review():
    pid = request.args.get('pid')
    referring_page = request.referrer
    return redirect(url_for('product_rating.delete_review', pid=pid, referring_page=referring_page))

# Deletes the review for the current user and product
@bp.route('/delete_pr/<int:pid>', methods=['POST'])
def delete_review(pid):
    uid = current_user.id
    try:
        # Query for deleting the review
        delete_query = '''
            DELETE FROM UserReviewsProduct 
            WHERE product_ID = :pid AND customer_ID = :uid
        '''
        app.db.execute(delete_query, pid=pid, uid=uid)

        # Redirect back to the product details page
        flash("Review deleted successfully!", "success")
        return redirect(url_for('product.detail', product_id=pid))

    except Exception as e:
        flash(f"Error deleting review: {e}", "danger")
        return redirect(url_for('product.detail', product_id=pid))


# Redirect for adding a new review
@bp.route('/redirect_to_add_review', methods=['GET', 'POST'])
def redirect_to_add_review():
    pid = request.args.get('pid')
    return redirect(url_for('product_rating.add_review', pid=pid))

# Get the current user ID for the add review page
@bp.route('/add_review/<int:pid>', methods=['GET', 'POST'])
def add_review(pid):
    uid = current_user.id   
    return render_template('add_product_review.html', pid=pid)

@bp.route('/insert_pr', methods=['POST'])
def insert_data():
    description = request.form.get('description')
    stars = request.form.get('stars')
    pid = request.form.get('pid')  # Product ID
    uid = current_user.id  # Current user ID

    try:
        # Check if the user can review the product
        if not Product.can_review_product(uid, pid):
            flash("You can only review products you have purchased.", "danger")
            return redirect(url_for('product.detail', product_id=pid))

        # Check if the user already reviewed this product
        existing_review = app.db.execute('''
            SELECT id 
            FROM UserReviewsProduct
            WHERE customer_id = :uid AND product_id = :pid
        ''', uid=uid, pid=pid)

        if existing_review:
            flash("You have already submitted a review for this product.", "warning")
            return redirect(url_for('product.detail', product_id=pid))

        # Validate inputs
        if not (1 <= int(stars) <= 5):
            flash("Rating must be between 1 and 5.", "danger")
            return redirect(url_for('product.detail', product_id=pid))

        if len(description) > 255:
            flash("Review exceeds the maximum length of 255 characters.", "danger")
            return redirect(url_for('product.detail', product_id=pid))

        # Insert review into the database
        insert_query = '''
            INSERT INTO UserReviewsProduct (customer_id, product_id, rating_message, rating_num, review_date)
            VALUES (:uid, :pid, :description, :stars, current_timestamp)
        '''
        app.db.execute(insert_query, uid=uid, pid=pid, description=description, stars=stars)

        flash("Review submitted successfully!", "success")
        return redirect(url_for('product.detail', product_id=pid))

    except Exception as e:
        flash(f"Error submitting review: {e}", "danger")
        return redirect(url_for('product.detail', product_id=pid))
