from flask import current_app as app

class Feedback:
    def __init__(self, id, customer_id, target_id, rating_num, rating_message, review_date, is_product=True):
        self.id = id
        self.customer_id = customer_id
        self.target_id = target_id  # Either product_id or seller_id
        self.rating_num = rating_num
        self.rating_message = rating_message
        self.review_date = review_date
        self.is_product = is_product  # To differentiate product and seller reviews

    # Method to get the 5 most recent feedback (for both products and sellers)
    @staticmethod
    def get_most_recent_feedback(user_id, limit=5):
        # Get all feedback for products (without limiting)
        product_reviews = app.db.execute('''
            SELECT id, customer_id, product_id, rating_num, rating_message, review_date, true as is_product
            FROM UserReviewsProduct
            WHERE customer_id = :user_id
            ORDER BY review_date DESC
        ''', user_id=user_id)
        # debug
        print({len(product_reviews)})

        # Get all feedback for sellers (without limiting)
        seller_reviews = app.db.execute('''
            SELECT id, customer_id, seller_id, rating_num, rating_message, review_date, false as is_product
            FROM UserReviewsSeller
            WHERE customer_id = :user_id
            ORDER BY review_date DESC
        ''', user_id=user_id)
        # debug
        print({len(seller_reviews)})

        # Combine the results
        reviews = product_reviews + seller_reviews

        # Sort the combined reviews by 'review_date' (6th column, so #5)
        reviews.sort(key=lambda x: x[5], reverse=True)

        # Return the 5 most recent feedback items
        return [Feedback(*row) for row in reviews[:limit]]
