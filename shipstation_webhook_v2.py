from flask import Flask, request, jsonify
import requests
import os
import traceback

app = Flask(__name__)

# Get your ShipStation V2 API token from environment variable
SHIPSTATION_ACCESS_TOKEN = os.getenv("SHIPSTATION_ACCESS_TOKEN")

@app.route('/push-to-shipstation', methods=['POST'])
def push_to_shipstation():
    try:
        # 🔍 Log raw incoming request body (useful for debugging)
        print("📥 Raw request body:")
        print(request.get_data(as_text=True))

        # 🔍 Parse JSON safely, even if Content-Type is wrong
        data = request.get_json(force=True)
        print("📥 Parsed JSON:")
        print(data)

        # ✅ Build order payload using .get() to avoid KeyErrors
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

        # 🔁 Send order to ShipStation
        response = requests.post(
            "https://api.shipstation.com/orders/createorder",
            json=order_payload,
            headers={
                "Authorization": f"Bearer {SHIPSTATION_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
        )

        # 📤 Log response from ShipStation
        print("📤 ShipStation response:", response.status_code, response.text)

        if response.status_code == 200:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": response.text}), 500

    except Exception as e:
        # 🔥 Catch and log any unexpected errors
        print("🔥 Uncaught Exception:")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 🔌 Start the app on correct host and port for Render
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
