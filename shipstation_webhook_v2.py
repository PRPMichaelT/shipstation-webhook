
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Bearer token from ShipStation (set in Render as an environment variable)
SHIPSTATION_ACCESS_TOKEN = os.getenv("SHIPSTATION_ACCESS_TOKEN")

@app.route('/push-to-shipstation', methods=['POST'])
def push_to_shipstation():
    data = request.json

    order_payload = {
        "orderNumber": data['invoice_id'],
        "orderDate": data['order_date'],
        "orderStatus": "awaiting_shipment",
        "customerEmail": data['customer_email'],
        "billTo": {
            "name": data['billing_name']
        },
        "shipTo": {
            "name": data['shipping_name'],
            "street1": data['shipping_address'],
            "city": data['shipping_city'],
            "state": data['shipping_state'],
            "postalCode": data['shipping_zip'],
            "country": "US"
        },
        "items": data['items']
    }

    response = requests.post(
        "https://api.shipstation.com/orders/createorder",
        json=order_payload,
        headers={
            "Authorization": f"Bearer {SHIPSTATION_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
    )

    if response.status_code == 200:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error", "message": response.text}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
