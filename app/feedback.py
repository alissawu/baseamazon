from flask import Blueprint, jsonify, render_template, request
from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
from .models.feedback import Feedback

bp = Blueprint('feedback', __name__)

@bp.route('/feedback/user', methods=['GET'])
def get_recent_feedback():
    user_id = request.args.get('acct_ID')
    sort_by = request.args.get("sort_by", "review_date")  # Default: review_date
    order = request.args.get("order", "desc")  # Default: descending

    items = Feedback.get_most_recent_feedback(user_id, sort_by=sort_by, order=order)
    return render_template('feedback.html', feedback_items=items, sort_by=sort_by, order=order)


@bp.route('/feedback/user_reviews', methods=['GET'])
def user_feedback():
    user_id = current_user.id
    # Always sort by date descending in the backend
    feedback_items = Feedback.get_all_feedback(user_id)
    return render_template('user_feedback.html', feedback_items=feedback_items)


@bp.route('/feedback/edit/<int:review_id>', methods=['POST'])
def edit_review(review_id):
    """
    Edit a review. Updates either a product or seller review based on is_product flag.
    """
    rating_num = request.form.get('rating_num', type=int)
    rating_message = request.form.get('rating_message', type=str)
    is_product = request.form.get('is_product', type=lambda x: x.lower() == 'true')  # Convert 'true'/'false' to bool

    try:
        Feedback.update_review(review_id, rating_num, rating_message, is_product)
        flash("Review updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating review: {e}", "danger")
    
    return redirect(url_for('feedback.user_feedback'))


@bp.route('/feedback/delete/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    try:
        Feedback.delete_review(review_id, current_user.id)
        flash("Review deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting review: {e}", "danger")
    
    # Redirect back to the user's feedback management page
    return redirect(url_for('feedback.user_feedback'))
