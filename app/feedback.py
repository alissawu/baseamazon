from flask import Blueprint, jsonify, render_template
from flask import current_app as app
from flask_login import current_user
from .models.feedback import Feedback

bp = Blueprint('feedback', __name__)

@bp.route('/feedback/<int:user_id>', methods=['GET'])
def get_recent_feedback(user_id):
    print(f"Requested user ID: {user_id}")  # debug
    
    # get all feedback items for the specified user
    items = Feedback.get_most_recent_feedback(user_id)
    print(f"Feedback items for user {user_id}: {items}")  # debug
    
    return render_template('feedback.html', feedback_items=items)