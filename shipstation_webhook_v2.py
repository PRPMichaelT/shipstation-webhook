from flask import Flask, request, jsonify
import requests
import os
import traceback

app = Flask(__name__)

# Get your ShipStation API token from environment variable
SHIPSTATION_ACCESS_TOKEN = os.getenv("SHIPSTATION_ACCESS_TOKEN")

@app.route('/push-to-shipstation', methods=['POST'])
def push_to_shipstation():
    print("🛬 Received POST request")  # NEW log line right away

    try:
        # Log the raw request body (even if not JSON)
        print("📥 Raw request body:")
        print(request.get_data(as_text=True))

        # Force-parse JSON body (even with incorrect headers)
        data = request.get_json(force=True)
        print("📥 Parsed JSON:")
        print(data)

        # Build order payload, safely using .get() to avoid crashes
        order_payload = {
            "orderNumber": data.get('invoice_id', 'UNKNOWN'),
            "orderDate": data.get('order_date', '2025-01-01'),
            "orderStatus": "awaiting_shipment",
            "customerEmail": data.get('customer_email', ''),
            "billTo": {
                "name": data.get('billing_name', '')
            },
            "shipTo": {
                "name": data.get('shipping_name', ''),
                "street1": data.get('shipping_address', ''),
                "city": data.get('shipping_city', ''),
                "state": data.get('shipping_state', ''),
                "postalCode": data.get('shipping_zip', ''),
                "country": "US"
            },
            "items": data.get('items', [])
        }

        # Send to ShipStation
        response = requests.post(
            "https://api.shipstation.com/orders/createorder",
            json=order_payload,
            headers={
                "Authorization": f"Bearer {SHIPSTATION_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
        )

        # Log response
        print("📤 ShipStation response:", response.status_code, response.text)

        if response.status_code == 200:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": response.text}), 500

    except Exception as e:
        print("🔥 Uncaught Exception:")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# Required for Render deployment
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
