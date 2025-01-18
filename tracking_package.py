from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import json

app = Flask(__name__)

chats = []
rescue_packages = []
users = []

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    user = data.get('user')

    if not user or not isinstance(user, dict):
        return jsonify({"error": "Invalid or missing user data"}), 400

    user_id = str(uuid.uuid4())
    user['id'] = user_id
    users.append(user)

    return jsonify({"message": "User added successfully", "user": user}), 200

@app.route('/get_users', methods=['GET'])
def get_users():
    return jsonify({"users": users}), 200

@app.route('/get_user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user}), 200

@app.route('/add_package', methods=['POST'])
def add_package():
    data = request.json
    package_info = data.get('package_info')

    if not package_info or not isinstance(package_info, dict):
        return jsonify({"error": "Invalid or missing package data"}), 400

    package_id = str(uuid.uuid4())
    package_info['id'] = package_id
    package_info['status'] = "Pending"
    package_info['created_at'] = datetime.utcnow().isoformat()
    rescue_packages.append(package_info)

    return jsonify({"message": "Package added successfully", "package": package_info}), 200

@app.route('/get_packages', methods=['GET'])
def get_packages():
    return jsonify({"packages": rescue_packages}), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    sender = data.get('sender')
    receivers = data.get('receivers')
    message = data.get('message')
    package_info = data.get('package_info')

    if not all([sender, receivers, message]):
        return jsonify({"error": "Missing sender, receivers, or message"}), 400

    if not isinstance(receivers, list) or not receivers:
        return jsonify({"error": "Receivers must be a non-empty list"}), 400

    chat_entries = []
    for receiver in receivers:
        chat_entry = {
            "sender": sender,
            "receiver": receiver,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        chats.append(chat_entry)
        chat_entries.append(chat_entry)

    if package_info:
        estimated_delivery_time = calculate_path_time(package_info, receivers)
        package_entry = {
            "package_info": package_info,
            "status": "In Transit",
            "estimated_delivery_time": estimated_delivery_time,
            "updated_at": datetime.utcnow().isoformat(),
            "sender": sender,
            "receivers": receivers
        }
        rescue_packages.append(package_entry)

    return jsonify({
        "message": "Messages sent successfully", 
        "chats": chat_entries, 
        "package_tracking": package_entry if package_info else None
    }), 200

def calculate_path_time(package_info, receivers):
    try:
        with open('packages.json', 'r') as file:
            data = json.load(file)
            for package in data:
                if package['sender'] == package_info['sender'] and package['receiver'] == package_info['receiver'] and package['resource'] == package_info['resource']:
                    return package.get('time', None)
    except FileNotFoundError:
        return None
    except KeyError:
        return None

@app.route('/get_messages', methods=['GET'])
def get_messages():
    user = request.args.get('user')

    if not user:
        return jsonify({"error": "Missing user parameter"}), 400

    user_chats = [chat for chat in chats if chat['sender']['id'] == user or chat['receiver']['id'] == user]
    return jsonify({"messages": user_chats}), 200

@app.route('/update_package_status', methods=['POST'])
def update_package_status():
    data = request.json
    package_info = data.get('package_info')
    status = data.get('status')

    if not all([package_info, status]):
        return jsonify({"error": "Missing package_info or status"}), 400

    for package in rescue_packages:
        if package['id'] == package_info.get('id'):
            package['status'] = status
            package['updated_at'] = datetime.utcnow().isoformat()
            return jsonify({"message": "Package status updated successfully", "package_info": package_info, "status": status}), 200

    return jsonify({"error": "Package not found"}), 404

@app.route('/get_package_status', methods=['GET'])
def get_package_status():
    package_id = request.args.get('package_id')

    if not package_id:
        return jsonify({"error": "Missing package_id parameter"}), 400

    package = next((p for p in rescue_packages if p['id'] == package_id), None)
    if not package:
        return jsonify({"error": "Package not found"}), 404

    return jsonify({"package": package}), 200

if __name__ == '__main__':
    app.run(debug=True)
