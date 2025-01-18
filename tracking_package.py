from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import json
import os
import subprocess

app = Flask(__name__)

chats = []
rescue_packages = []
users = []

# Load data from JSON files
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

locations = load_json('locations.json')
resources = load_json('resources.json')
deliveries = load_json('deliveries.json')
names = load_json('names.json')

@app.route('/get_paths', methods=['GET'])
def get_paths():
    paths = [delivery['path'] for delivery in deliveries]
    return jsonify(paths), 200

@app.route('/request_resources', methods=['POST'])
def request_resources():
    data = request.json
    sender = data.get('sender')
    name = data.get('name')
    amount = data.get('amount')

    if not all([sender, name, amount]):
        return jsonify({"error": "Missing sender, name, or amount"}), 400

    receiver_needs = [{"name": sender, "needs": {name: amount}}]
    result = subprocess.run(['python3', 'UpdateResources.py', '--receiver_needs', json.dumps(receiver_needs)], capture_output=True, text=True)

    if result.returncode != 0:
        return jsonify({"error": "Failed to update resources", "details": result.stderr}), 500

    return jsonify({"message": "Resources requested successfully"}), 200

@app.route('/add_resources', methods=['POST'])
def add_resources():
    data = request.json
    sender = data.get('sender')
    name = data.get('name')
    amount = data.get('amount')

    if not all([sender, name, amount]):
        return jsonify({"error": "Missing sender, name, or amount"}), 400

    sender_resources = [{"name": sender, "resources": {name: amount}}]
    result = subprocess.run(['python3', 'UpdateResources.py', '--sender_resources', json.dumps(sender_resources)], capture_output=True, text=True)

    if result.returncode != 0:
        return jsonify({"error": "Failed to update resources", "details": result.stderr}), 500

    return jsonify({"message": "Resources added successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/get_users', methods=['POST'])
def get_users():
    # Call merge_json.py
    result = subprocess.run(['python3', 'merge_json.py'], capture_output=True, text=True)
    
    if result.returncode != 0:
        return jsonify({"error": "Failed to merge data", "details": result.stderr}), 500

    # Load the merged data from people_data.json
    people_data = load_json('people_data.json')
    
    return jsonify(people_data), 200

@app.route('/add_name', methods=['POST'])
def add_user():
    data = request.json
    user_name = data.get('name')
    user_x = data.get('x')
    user_y = data.get('y')
    user_role = data.get('role')

    if not user_name or not user_x or not user_y or not user_role:
        return jsonify({"error": "Invalid or missing user data"}), 400

    # Call UpdateLocations.py to add the user
    if (user_role == 'camp'):
        result = subprocess.run(['python3', 'UpdateLocations.py', '--add_receivers', json.dumps([{"name": user_name, "x": user_x, "y": user_y}])], capture_output=True, text=True)
    else:
        result = subprocess.run(['python3', 'UpdateLocations.py', '--add_senders', json.dumps([{"name": user_name, "x": user_x, "y": user_y}])], capture_output=True, text=True)
    if "has already been taken" in result.stdout:
        return jsonify({"error": f"User name '{user_name}' has already been taken"}), 400

    return jsonify({"message": "User added successfully", "user": user_name}), 200

@app.route('/get_user/<user_name>', methods=['GET'])
def get_user_by_name(user_name):
    # Load the merged data from people_data.json
    people_data = load_json('people_data.json')
    
    # Search for the user in senders and receivers
    user = next((user for user in people_data['senders'] if user['name'] == user_name), None)
    if not user:
        user = next((user for user in people_data['receivers'] if user['name'] == user_name), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user}), 200

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
        for delivery in deliveries:
            if delivery['sender'] == package_info['sender'] and delivery['receiver'] == package_info['receiver'] and delivery['resource'] == package_info['resource']:
                return delivery.get('time', None)
    except KeyError:
        return None

@app.route('/get_messages', methods=['GET'])
def get_messages():
    user = request.args.get('user')

    if not user:
        return jsonify({"error": "Missing user parameter"}), 400

    user_chats = [chat for chat in chats if chat['sender'] == user or chat['receiver'] == user]
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