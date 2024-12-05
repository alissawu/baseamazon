from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal


from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, account_balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.account_balance = account_balance
    
    def deposit(self, amount):
        """
        Deposit money to the user's account.
        """
        if amount <= 0:
            print("Deposit amount must be greater than zero.")
            return False
        
        try:
            amount_decimal = Decimal(amount)  # Convert to Decimal
            app.db.execute("""
            UPDATE Users
            SET account_balance = account_balance + :amount
            WHERE id = :id
            """, amount=amount_decimal, id=self.id)
            self.account_balance += amount_decimal  # Update the in-memory balance
            return True
        except Exception as e:
            print(f"Error during deposit: {e}")
            return False
    
    def withdraw(self, amount):
        """
        Withdraw money from the user's account if balance is sufficient.
        """
        if amount <= 0:
            print("Withdrawal amount must be greater than zero.")
            return False
        if self.account_balance < amount:
            print("Insufficient balance.")
            return False
        try:
            amount_decimal = Decimal(amount)  # Convert to Decimal
            app.db.execute("""
            UPDATE Users
            SET account_balance = account_balance - :amount
            WHERE id = :id
            """, amount=amount_decimal, id=self.id)
            self.account_balance -= amount_decimal  # Update the in-memory balance
            return True
        except Exception as e:
            print(f"Error during withdrawal: {e}")
            return False

    def purchase(self, cost):
        """
        Deduct money from the user's account for a purchase if balance is sufficient.
        """
        if cost <= 0:
            print("Purchase amount must be greater than zero.")
            return False
        if self.account_balance < cost:
            print("Insufficient balance for purchase.")
            return False
        try:
            app.db.execute("""
            UPDATE Users
            SET account_balance = account_balance - :cost
            WHERE id = :id
            """, cost=cost, id=self.id)
            self.account_balance -= cost  # Update the in-memory balance
            return True
        except Exception as e:
            print(f"Error during purchase: {e}")
            return False

    def update_account(self, new_email=None, new_password=None, new_firstname = None, new_lastname = None):
        """
        Update the user's email and/or password in the database.
        """
        updates = {}
        if new_email:
            updates['email'] = new_email
        if new_password:
            updates['password'] = generate_password_hash(new_password)
        if new_firstname:
            updates['firstname'] = new_firstname
        if new_lastname:
            updates['lastname'] = new_lastname

        if updates:
            try:
                app.db.execute(f"""
                UPDATE Users
                SET {', '.join([f"{key} = :{key}" for key in updates.keys()])}
                WHERE id = :id
                """,
                id=self.id,
                **updates)
                # Update the in-memory object
                if new_email:
                    self.email = new_email
                if new_firstname:
                    self.firstname = new_firstname
                if new_lastname:
                    self.lastname = new_lastname
                return True
            except Exception as e:
                print(f"Error updating user account: {e}")
                return False
        return False

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, account_balance
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname, account_balance)
VALUES(:email, :password, :firstname, :lastname, :account_balance)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname,
                                  account_balance = 0.00)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, account_balance
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None
