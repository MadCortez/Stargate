from flask import Flask, request, jsonify, make_response
import requests
import zlib

app = Flask(__name__)

# Function to get rates on given date
def fetch_currency_rates(date):
    url = f"https://www.nbrb.by/api/exrates/rates?ondate={date}&periodicity=0"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Endpoint with input data
@app.route('/rates', methods=['GET'])
def get_rates():
    date = request.args.get('date')
    if not date:
        return make_response(jsonify({"error": "Date is required"}), 400)
    
    data = fetch_currency_rates(date)
    if data:
        response = make_response(jsonify({"status": "success", "data": data}))
    else:
        response = make_response(jsonify({"status": "failure", "message": "Data could not be loaded"}))
    
    crc32_value = zlib.crc32(response.get_data()).__str__()
    response.headers['CRC32'] = crc32_value
    return response

if __name__ == '__main__':
    app.run(debug=True)