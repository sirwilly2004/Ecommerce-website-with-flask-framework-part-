from flask import Blueprint, render_template, flash, redirect, url_for
from .forms import LoginForm, SignUpForm, PasswordChangeForm
from .models import Customer
from flask_login import login_user, login_required, logout_user
from . import db


auth = Blueprint('auth', __name__)

@auth.route('/')
def home_page():
    return render_template('home.html')

@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        customer = Customer.query.filter_by(email=email).first()
        if customer:
            if customer.verify_password(password=password):
                login_user(customer)
                flash('You have been logged in. Enjoy your shopping with us', 'success')  
                return redirect('/')
            else:
                flash('Incorrect Email or Password', 'danger') 
        else:
            flash('Account does not exist, please Sign Up', 'warning')
    return render_template('login.html', form=form)

@auth.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        existing_email = Customer.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('This email has been used. Try another email or login instead.', 'warning')
            return redirect(url_for('auth.sign_up'))
        else:
            customer = Customer(email=form.email.data, username=form.username.data)
            customer.password = form.password1.data
            try:
                db.session.add(customer)
                db.session.commit()
                flash('Account created successfully. You can now login.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                print(e)
                flash('Account not created! Please try again.', 'danger')
    return render_template('sign_up.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are been logged out')
    return redirect('/')

@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    return render_template('profile.html', customer=customer)

@auth.route('/change_password/<int:customer_id>', methods=['POST', 'GET'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)
    if form.validate_on_submit():
        if customer.verify_password(password=form.old_password.data):
            # Update the password
            customer.password = form.new_password.data
            db.session.commit()
            flash('Password Changed Successfully', 'success')
            return redirect(url_for('auth.profile', customer_id=customer_id))
        else:
            flash('Old Password is Incorrect. Insert the correct password', 'danger')
            return redirect(url_for('auth.change_password', customer_id=customer_id))
    return render_template('change_password.html', form=form, customer=customer)

