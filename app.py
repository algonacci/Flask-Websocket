from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


def read_data():
    data = []
    with open('data.txt', 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # Skip the header line
            values = line.strip().split()
            data.append({
                'Timestamp': values[2],
                'Temperature (°C)': float(values[0]),
                'Humidity (%)': int(values[1]),
            })
    return data


@app.route("/")
def index():
    data = read_data()
    return render_template("index.html", data=data)


@app.route("/api/add_data", methods=["POST"])
def add_data():
    try:
        new_data = request.get_json()
        if new_data:
            timestamp = new_data["timestamp"]
            temperature = new_data["temperature"]
            humidity = new_data["humidity"]

            with open('data.txt', 'a') as file:
                file.write(f"{temperature} {humidity} {timestamp}\n")

            data = read_data()
            socketio.emit('update data', {'data': data})

            return jsonify({
                "message": "Data added successfully"
            }), 201
        else:
            return jsonify({
                "error": "Invalid JSON data"
            }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@socketio.on('connect')
def test_connect():
    emit('after connect', {'data': 'Connected'})


@socketio.on('request data')
def handle_request_data():
    data = read_data()
    emit('update data', {'data': data})


if __name__ == "__main__":
    socketio.run(app)
