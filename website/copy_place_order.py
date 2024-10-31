@views.route('/place-order', methods=['POST','GET'])
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
    if customer_cart:
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price * item.quantity
            
            total_in_kobo = total * 100  # Assuming total is in Naira so we need to convert to kobo = 100 kobo is #1
            
            # Prepare data for Paystack
            data = {
                "email": current_user.email,  # Customer's email
                "amount": total_in_kobo,  # Amount in kobo
                "currency": "NGN", 
            }

            # Make the request to Paystack
            response = requests.post(URL, json=data, headers=HEADERS)
            if response.status_code == 200:
                response_data = response.json()
                authorization_url = response_data['data']['authorization_url']
                reference = response_data['data']['reference']

                # Create new orders in your database
                for item in customer_cart:
                    new_order = Order()
                    new_order.quantity = item.quantity
                    new_order.price = item.product.current_price
                    new_order.status = 'Pending'  # Set initial status to Pending
                    new_order.payment_id = reference  # Store the payment reference
                    new_order.product_link = item.product_link
                    new_order.customer_link = item.customer_link

                    db.session.add(new_order)

                    # Update product stock
                    product = Product.query.get(item.product_link)
                    product.in_stock -= item.quantity
                
                # Clear the cart
                for item in customer_cart:
                    db.session.delete(item)

                db.session.commit()

                flash('Order Placed Successfully. Redirecting to payment...')
                return redirect(authorization_url)  # Redirect to Paystack payment page
            else:
                print("Error initializing transaction:", response.json())
                flash('Error initializing payment. Please try again.')
                return redirect('/')

        except Exception as e:
            print(e)
            flash('Order not placed due to an error.')
            return redirect('/')
    else:
        flash('Your cart is empty.')
        return redirect('/')

@views.route('/payment-callback', methods=['GET'])
def payment_callback():
    payment_reference = request.args.get('reference')  # Get the reference from the query parameters

    # Verify the payment with Paystack
    verification_url = f'https://api.paystack.co/transaction/verify/{payment_reference}'
    headers = {
        'Authorization': f'Bearer {API_KEY}',  # Use your API key
    }
    
    response = requests.get(verification_url, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        if response_data['data']['status'] == 'success':
            # Update the order status in your database
            order = Order.query.filter_by(payment_id=payment_reference).first()
            if order:
                order.status = 'Paid'  # Update order status
                db.session.commit()
                flash('Payment successful! Your order is confirmed.')
            return redirect('/place-order')  # Redirect to orders page
        else:
            flash('Payment failed or was not successful.')
            return redirect('/')
    else:
        flash('Error verifying payment. Please try again.')
        return redirect('/')



