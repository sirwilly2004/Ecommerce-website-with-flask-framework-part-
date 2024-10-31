from flask import Blueprint, render_template, send_from_directory, flash, url_for, redirect, request, jsonify
from .models import Product,Cart,Order
from flask_login import login_required,current_user
from . import db
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_PUBLISHABLE_KEY_PAYSTACK = os.getenv('API_PUBLISHABLE_KEY_PAYSTACK')
URL = os.getenv('URL')
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}



views = Blueprint('views', __name__)

@views.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

@views.route('/')
def home():
    items = Product.query.filter_by(flash_sale=True)

    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity += 1
            db.session.commit()
            flash(f' Quantity of { item_exists.product.product_name } has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print(e)
            flash(f'Quantity of { item_exists.product.product_name } not updated')
            return redirect(request.referrer)
        # the product.product_name is the backref use in the product table model to reference the product table with the other table that has a relationship with the it using the foreignkey

        
    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} has been added to cart')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'{new_cart_item.product.product_name} has not been added to cart')
    return redirect(request.referrer)


@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount +=item.product.current_price * item.quantity

    return render_template('cart.html', cart=cart , amount=amount , total = amount + 200 )

@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity - 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)

@views.route('/place-order', methods=['POST','GET'])
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
    if customer_cart:
        try:
            # Calculate total amount in kobo
            total = sum(item.product.current_price * item.quantity for item in customer_cart) * 100
            
            # Prepare data for Paystack
            data = {
                "email": current_user.email,  # Customer's email
                "amount": total,  # Amount in kobo
                "currency": "NGN", 
            }

            # Make request to Paystack for payment initiation
            response = requests.post(URL, json=data, headers=HEADERS)
            if response.status_code == 200:
                response_data = response.json()
                authorization_url = response_data['data']['authorization_url']
                reference = response_data['data']['reference']

                # Flash message to indicate redirection
                flash('Redirecting to payment page...')
                return redirect(authorization_url)
            else:
                flash('Error initializing payment. Please try again.')
                return redirect('/')
        except Exception as e:
            flash('Order could not be placed due to an error.')
            return redirect('/')
    else:
        flash('Your cart is empty.')
        return redirect('/')


@views.route('/payment-callback', methods=['GET'])
def payment_callback():
    payment_reference = request.args.get('reference')  # Get the reference from query parameters

    # Verify payment with Paystack
    verification_url = f'https://api.paystack.co/transaction/verify/{payment_reference}'
    headers = {
        'Authorization': f'Bearer {API_KEY}',  # Use your API key
    }
    
    response = requests.get(verification_url, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        if response_data['data']['status'] == 'success':
            # Payment confirmed; now create the order
            customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
            for item in customer_cart:
                new_order = Order(
                    quantity=item.quantity,
                    price=item.product.current_price,
                    status='Paid',  # Set status to Paid
                    payment_id=payment_reference,  # Store payment reference
                    product_link=item.product_link,
                    customer_link=item.customer_link
                )
                db.session.add(new_order)

                # Update product stock
                product = Product.query.get(item.product_link)
                product.in_stock -= item.quantity

            # Clear the cart
            Cart.query.filter_by(customer_link=current_user.id).delete()
            db.session.commit()
            flash('Payment successful! Your order is confirmed.')
            return redirect('/order')
        else:
            flash('Payment failed or was not successful.')
            return redirect('/')
    else:
        flash('Error verifying payment. Please try again.')
        return redirect('/')


@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)

@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')

