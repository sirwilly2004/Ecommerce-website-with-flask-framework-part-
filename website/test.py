# from intasend import APIService

# API_PUBLISHABLE_KEY = 'ISPubKey_test_7f02b34f-b6ea-474f-a620-f9805f43b080'
# API_SECRET_KEY = 'ISPubKey_test_7f02b34f-b6ea-474f-a620-f9805f43b080'

# service = APIService(token=API_SECRET_KEY, publishable_key=API_PUBLISHABLE_KEY, test=True)

# create_order_response = service.collect.mpesa_stk_push(
#     phone_number= '9066213037',
#     email= 'williamsolaolu2004@gmail.com',
#     amount=500,
#     narrative= 'Purchase of goods')

# print(create_order_response)

import requests

# Your Paystack Test Secret Key
API_PUBLISHABLE_KEY_PAYSTACK = 'pk_scecret for me 0f'
API_KEY = 'sk_testsecret for the using paystact08672c'
# Paystack API endpoint for initializing a transaction
url = 'https://api.paystack.co/transaction/initialize'

# Sample transaction data
data = {
    "email": "williamyourgmail@gmail.com",  # Customer's email
    "amount": 500,  # Amount in kobo (50000 kobo = 500 Naira)
    "currency": "NGN",  # Currency code
}

# Set up headers with your API key
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Make the request to Paystack
response = requests.post(url, json=data, headers=headers)
# Check the response
if response.status_code == 200:
    print("Transaction initialized successfully!")
    response_data = response.json()
    
    # Accessing the required fields
    # authorization_url = response_data['data']['authorization_url']
    # access_code = response_data['data']['access_code']
    # reference = response_data['data']['reference']
    # Output the extracted values
    # print("Authorization URL:", authorization_url)
    # print("Access Code:", access_code)
    print("Responses:", response_data)
else:
    print("Error initializing transaction:", response.json())


