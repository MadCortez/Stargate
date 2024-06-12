from flask import Flask, request, jsonify, make_response
import requests
import zlib
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Function to get previous day
def get_previos_day(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    previous_day = date_obj - timedelta(days = 1)
    return previous_day.strftime("%Y-%m-%d")

# Function to create database sqlite
def create_database():
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        method TEXT NOT NULL,
                        endpoint TEXT NOT NULL,
                        request_data TEXT,
                        response_data TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
    conn.commit()
    conn.close()

# Function to log
def log_request_response(method, endpoint, request_data, response_data):
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO logs (method, endpoint, request_data, response_data)
                      VALUES (?, ?, ?, ?)''',
                   (method, endpoint, request_data, response_data))
    conn.commit()
    conn.close()

# Function to get rates on given date
def fetch_currency_rates(date):
    url = f"https://www.nbrb.by/api/exrates/rates?ondate={date}&periodicity=0"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to get rate by date and code
def fetch_currency_rate_by_code(date, code):
    url = f"https://www.nbrb.by/api/exrates/rates/{code}?ondate={date}&periodicity=0"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
# Function to get dynamics by start_date, end_date and code
def fetch_dynamics(start_date, end_date, code):
    url = f"https://www.nbrb.by/api/exrates/rates/dynamics/{code}?startdate={start_date}&enddate={end_date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to get all logs
def get_all_logs():
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs')
    logs = cursor.fetchall()
    conn.close()
    return logs

# Function to get dynamics
def get_dynamics(date, code):
    dynamics = fetch_dynamics(get_previos_day(date), date, code)
    if dynamics:
        rate_change = dynamics[-1]['Cur_OfficialRate'] - dynamics[0]['Cur_OfficialRate']
        return rate_change
    else:
        return None

# Endpoint with input data
@app.route('/rates', methods=['GET'])
def get_rates():
    date = request.args.get('date')
    if not date:
        return make_response(jsonify({"error": "Date is required"}), 400)
    
    log_request_response(request.method, '/rates', f"date:{date}", None)

    data = fetch_currency_rates(date)
    if data:
        response = make_response(jsonify({"status": "success", "data": data}))
    else:
        response = make_response(jsonify({"status": "failure", "message": "Data could not be loaded"}))
    
    log_request_response(request.method, '/rates', f"date:{date}", response.get_data(as_text=True))

    crc32_value = zlib.crc32(response.get_data()).__str__()
    response.headers['CRC32'] = crc32_value
    return response

# Endpoint with input data and code
@app.route("/rate", methods=['GET'])
def get_rate_by_code():
    date = request.args.get('date')
    code = request.args.get('code')
    if (not date) or (not code):
        return make_response(jsonify({"error": "Date and code are required"}), 400)
    
    log_request_response(request.method, '/rate', f"date:{date}, code:{code}", None)

    data = fetch_currency_rate_by_code(date, code)
    if data:
        response_data = {"status": "success", "data": data}
        dynamics = get_dynamics(date, code)
        if dynamics is not None:
            response_data["dynamics"] = dynamics
        response = make_response(jsonify(response_data))
    else:
        response = make_response(jsonify({"status": "failure", "message": "Data could not be loaded"}))

    log_request_response(request.method, '/rate', f"date:{date}, code:{code}", response.get_data(as_text=True))

    crc32_value = zlib.crc32(response.get_data()).__str__()
    response.headers['CRC32'] = crc32_value
    return response

# Endpoint to view logs
@app.route('/logs', methods=['GET'])
def view_logs():
    logs = get_all_logs()
    return jsonify(logs)

if __name__ == '__main__':
    create_database()
    app.run(debug=True)