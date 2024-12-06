from flask import Blueprint, jsonify, render_template, request
from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import current_user
from .models.feedback import Feedback

bp = Blueprint('feedback', __name__)

@bp.route('/feedback/user', methods=['GET'])
def get_recent_feedback():
    user_id = request.args.get('acct_ID')
    print(f"Requested user ID: {user_id}")  # debug
    
    # get all feedback items for the specified user
    items = Feedback.get_most_recent_feedback(user_id)
    print(f"Feedback items for user {user_id}: {items}")  # debug

    
    return render_template('feedback.html', feedback_items=items)

@bp.route('/feedback/user_reviews', methods=['GET'])
def user_feedback():
    # Get all feedback items for the current user
    user_id = current_user.id
    feedback_items = Feedback.get_all_feedback(user_id)
    
    return render_template('user_feedback.html', feedback_items=feedback_items)

@bp.route('/feedback/edit/<int:review_id>', methods=['POST'])
def edit_review(review_id):
    # Retrieve the updated data from the form
    rating_num = request.form.get('rating_num')
    rating_message = request.form.get('rating_message')

    try:
        # Update the review in the database
        Feedback.update_review(review_id, rating_num, rating_message)
        flash("Review updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating review: {e}", "danger")
    
    # Redirect back to the user's feedback management page
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
