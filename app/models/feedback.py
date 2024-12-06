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
        # Use UNION ALL to combine product and seller reviews
        reviews = app.db.execute('''
            (
                SELECT id, customer_id, product_id AS target_id, rating_num, rating_message, review_date, true AS is_product
                FROM UserReviewsProduct
                WHERE customer_id = :user_id
            )
            UNION ALL
            (
                SELECT id, customer_id, seller_id AS target_id, rating_num, rating_message, review_date, false AS is_product
                FROM UserReviewsSeller
                WHERE customer_id = :user_id
            )
            ORDER BY review_date DESC
            LIMIT :limit
        ''', user_id=user_id, limit=limit)

        # Return the most recent feedback items
        return [Feedback(*row) for row in reviews]
    
    @staticmethod
    def get_all_feedback(user_id):
        # Combine product and seller reviews
        reviews = app.db.execute('''
            (
                SELECT id, customer_id, product_id AS target_id, rating_num, rating_message, review_date, true AS is_product
                FROM UserReviewsProduct
                WHERE customer_id = :user_id
            )
            UNION ALL
            (
                SELECT id, customer_id, seller_id AS target_id, rating_num, rating_message, review_date, false AS is_product
                FROM UserReviewsSeller
                WHERE customer_id = :user_id
            )
            ORDER BY review_date DESC
        ''', user_id=user_id)

        # Return all feedback items
        return [Feedback(*row) for row in reviews]


    @staticmethod
    def get_review_by_id(review_id):
        row = app.db.execute('''
            SELECT id, customer_id, target_id, rating_num, rating_message, review_date, is_product
            FROM (
                SELECT id, customer_id, product_id AS target_id, rating_num, rating_message, review_date, true AS is_product
                FROM UserReviewsProduct
                UNION ALL
                SELECT id, customer_id, seller_id AS target_id, rating_num, rating_message, review_date, false AS is_product
                FROM UserReviewsSeller
            ) AS combined_reviews
            WHERE id = :review_id
        ''', review_id=review_id)

        return Feedback(*row[0]) if row else None

    @staticmethod
    def update_review(review_id, rating_num, rating_message):
        # Check if the review is for a product or a seller
        product_review = app.db.execute('''
            SELECT id FROM UserReviewsProduct WHERE id = :review_id
        ''', review_id=review_id)
        
        if product_review:
            # Update the product review
            app.db.execute('''
                UPDATE UserReviewsProduct
                SET rating_num = :rating_num, rating_message = :rating_message
                WHERE id = :review_id
            ''', review_id=review_id, rating_num=rating_num, rating_message=rating_message)
        else:
            # Update the seller review
            app.db.execute('''
                UPDATE UserReviewsSeller
                SET rating_num = :rating_num, rating_message = :rating_message
                WHERE id = :review_id
            ''', review_id=review_id, rating_num=rating_num, rating_message=rating_message)


    @staticmethod
    def delete_review(review_id, user_id):
        # Attempt to delete from products first
        rows_deleted = app.db.execute('''
            DELETE FROM UserReviewsProduct
            WHERE id = :review_id AND customer_id = :user_id
        ''', review_id=review_id, user_id=user_id)
        
        # If no rows were deleted, attempt to delete from sellers
        if rows_deleted == 0:
            app.db.execute('''
                DELETE FROM UserReviewsSeller
                WHERE id = :review_id AND customer_id = :user_id
            ''', review_id=review_id, user_id=user_id)
