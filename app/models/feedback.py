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
    
    @staticmethod
    def get_all_feedback_by_customer_id(customer_id):
        rows = app.db.execute('''
            (
                SELECT id, customer_id, product_id AS target_id, rating_num, rating_message, review_date, true AS is_product
                FROM UserReviewsProduct
                WHERE customer_id = :customer_id
            )
            UNION ALL
            (
                SELECT id, customer_id, seller_id AS target_id, rating_num, rating_message, review_date, false AS is_product
                FROM UserReviewsSeller
                WHERE customer_id = :customer_id
            )
            ORDER BY review_date DESC
        ''', customer_id=customer_id)

        return [Feedback(*row) for row in rows]

    # Method to get the 5 most recent feedback (for both products and sellers)
    @staticmethod
    def get_most_recent_feedback(user_id, limit=5, sort_by="review_date", order="desc"):
        valid_columns = ["review_date", "rating_num"]
        if sort_by not in valid_columns:
            sort_by = "review_date"  # Default sort column

        sort_order = "DESC" if order.lower() == "desc" else "ASC"

        reviews = app.db.execute(f'''
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
            ORDER BY {sort_by} {sort_order}
            LIMIT :limit
        ''', user_id=user_id, limit=limit)

        return [Feedback(*row) for row in reviews]

    @staticmethod
    def get_all_feedback(user_id):
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
    def update_review(review_id, rating_num, rating_message, is_product):
        """
        Update a review in the database. Uses is_product to determine the table to update.

        Args:
            review_id (int): The ID of the review.
            rating_num (int): The new rating value.
            rating_message (str): The new review message.
            is_product (bool): True if the review is for a product, False if for a seller.
        """
        if is_product:
            # Update the product review
            app.db.execute('''
                UPDATE UserReviewsProduct
                SET rating_num = :rating_num, 
                    rating_message = :rating_message, 
                    review_date = current_timestamp
                WHERE id = :review_id
            ''', review_id=review_id, rating_num=rating_num, rating_message=rating_message)
        else:
            # Update the seller review
            app.db.execute('''
                UPDATE UserReviewsSeller
                SET rating_num = :rating_num, 
                    rating_message = :rating_message, 
                    review_date = current_timestamp
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
