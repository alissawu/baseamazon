from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional

from .models.user import User
from app import db  # Ensure db is imported correctly

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ProfileForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_email = StringField('New Email', validators=[Optional(), Email()])
    new_password = PasswordField('New Password', validators=[Optional()])
    new_firstname = StringField('New First Name', validators=[Optional()])
    new_lastname = StringField('New Last Name', validators=[Optional()])
    submit = SubmitField('Update Profile')

@bp.route('/deposit', methods=['POST'])
@login_required
def deposit():
    amount = request.form.get('amount', type=float)
    if amount and amount > 0:
        try:
            success = current_user.deposit(amount)
            if success:
                flash(f"Deposited {amount:.2f} successfully.", "success")
            else:
                flash("Failed to deposit due to an internal error.", "error")
        except Exception as e:
            flash(f"Unexpected error during deposit: {e}", "error")
    else:
        flash("Invalid deposit amount.", "error")
    return redirect(url_for('users.update_account'))


@bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    amount = request.form.get('amount', type=float)
    if amount and amount > 0:
        if current_user.withdraw(amount):
            flash(f"Withdrew {amount:.2f} successfully.", "success")
        else:
            flash("Insufficient balance or failed to withdraw.", "error")
    else:
        flash("Invalid withdrawal amount.", "error")
    return redirect(url_for('users.update_account'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def update_account():
    form = ProfileForm()
    if form.validate_on_submit():
        new_email = form.new_email.data
        new_password = form.new_password.data
        new_firstname = form.new_firstname.data
        new_lastname = form.new_lastname.data

        # Validate current password
        user = User.get_by_auth(current_user.email, form.current_password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.update_account'))
        # Update email if provided
        if new_email:
            current_user.email = new_email

        # Update password if provided
        if new_password:
            current_user.password = generate_password_hash(new_password)
        
        if new_firstname:
            current_user.firsname = new_firstname

        if new_lastname:
            current_user.firsname = new_lastname

        success = current_user.update_account(new_email=new_email, new_password=new_password, new_firstname=new_firstname, new_lastname=new_lastname)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')
        if not success:
            flash('Update failed, please try again.')
            return redirect(url_for('users.update_account'))
        try:
            return redirect(next_page)
        except Exception as e:
            flash(f"Error updating account: {e}", "error")
        return redirect(next_page)
    return render_template('profile.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('A user with this email already exists.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(
            form.email.data, form.password.data, form.firstname.data, form.lastname.data
        ):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))