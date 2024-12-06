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
    # Pagination
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE

    # Count total reviews by current user
    total_result = app.db.execute('SELECT COUNT(*) AS total_count FROM UserReviewsProduct WHERE customer_ID = :uid', uid=current_user.id)
    total = total_result[0][0] if total_result else 0

    # Ensure user is in the database
    count = len(app.db.execute('SELECT id FROM Users WHERE id = :uid', uid=current_user.id))
    if count > 0:
        # Get all product reviews for the current user
        reviews = app.db.execute('''
            SELECT urp.product_ID, urp.rating_message, urp.rating_num, urp.review_date, p.name 
            FROM UserReviewsProduct urp
            JOIN Products p ON p.product_ID = urp.product_ID
            WHERE urp.customer_ID = :uid
            ORDER BY urp.review_date DESC
            LIMIT :limit OFFSET :offset
        ''', uid=current_user.id, limit=PER_PAGE, offset=offset)
    else:
        reviews = None

    # Render the HTML file for product ratings
    return render_template('product_rating.html', reviews=reviews, total=total, page=page, per_page=PER_PAGE)

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
@bp.route('/update_pr', methods=['GET', 'POST'])
def update_data():
    # Get values for updating the review
    description = request.form.get('description')
    stars = request.form.get('stars')
    uid = current_user.id
    pid = request.form.get('pid')
    referring_page = request.form.get('referring_page')
    image_url = request.form.get('image_url')

    # Query for updating the review
    update_query = '''
        UPDATE UserReviewsProduct 
        SET rating_message = :description, rating_num = :stars, image_url = :image_url 
        WHERE product_ID = :pid AND customer_ID = :uid
    '''
    app.db.execute(update_query, description=description, stars=stars, pid=pid, uid=uid, image_url=image_url)

    # Redirect depending on where the user came from
    if 'product_rating' in referring_page:
        return redirect(url_for('product_rating.product_rating'))
    else:
        return redirect(url_for('products.product_details', pid=pid))

# Redirect to delete a review
@bp.route('/redirect_to_delete_review', methods=['GET', 'POST'])
def redirect_to_delete_review():
    pid = request.args.get('pid')
    referring_page = request.referrer
    return redirect(url_for('product_rating.delete_review', pid=pid, referring_page=referring_page))

# Deletes the review for the current user and product
@bp.route('/delete_pr/<int:pid>', methods=['GET', 'POST'])
def delete_review(pid):
    uid = current_user.id
    referring_page = request.args.get('referring_page')

    # Query for deleting the review
    delete_query = '''
        DELETE FROM UserReviewsProduct 
        WHERE product_ID = :pid AND customer_ID = :uid
    '''
    app.db.execute(delete_query, pid=pid, uid=uid)

    # Redirect depending on where the user came from
    if 'product_rating' in referring_page:
        return redirect(url_for('product_rating.product_rating'))
    else:
        return redirect(url_for('products.product_details', pid=pid))

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
    # Validate and insert review
    description = request.form.get('description')
    stars = request.form.get('stars')
    pid = request.form.get('pid')  # Product ID
    uid = current_user.id  # Current user ID

    try:
        # Validate inputs
        if not (1 <= int(stars) <= 5):
            flash("Rating must be between 1 and 5.", "danger")
            return redirect(url_for('product.detail', product_id=pid))  # Redirect to product page

        if len(description) > MAX_DESCRIPTION_LENGTH:
            flash(f"Review exceeds the maximum length of {MAX_DESCRIPTION_LENGTH} characters.", "danger")
            return redirect(url_for('product.detail', product_id=pid))

        # Insert review into the database
        insert_query = '''
            INSERT INTO UserReviewsProduct (customer_ID, product_ID, rating_message, rating_num, review_date)
            VALUES (:uid, :pid, :description, :stars, current_timestamp)
        '''
        app.db.execute(insert_query, uid=uid, pid=pid, description=description, stars=stars)

        # Redirect to product details page with success message
        flash("Review submitted successfully!", "success")
        return redirect(url_for('product.detail', product_id=pid))

    except Exception as e:
        flash(f"Error submitting review: {e}", "danger")
        return redirect(url_for('product.detail', product_id=pid))  # Redirect on failure

