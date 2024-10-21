from flask import Blueprint, jsonify
from flask import current_app as app

bp = Blueprint('feedback', __name__)

@bp.route('/feedback/<int:user_id>', methods=['GET'])
def get_recent_feedback(user_id):
    # Run the SQL query
    rows = app.db.execute('''
        (
            SELECT customer_id, product_id as item_id, rating_num, rating_message, review_date, 'product' as type
            FROM UserReviewsProduct
            WHERE customer_id = :user_id
        )
        UNION ALL
        (
            SELECT customer_id, seller_id as item_id, rating_num, rating_message, review_date, 'seller' as type
            FROM UserReviewsSeller
            WHERE customer_id = :user_id
        )
        ORDER BY review_date DESC
        LIMIT 5;
    ''', user_id=user_id)

    # Convert rows into a list of dictionaries
    feedback = [dict(row) for row in rows]
    
    return jsonify(feedback)
