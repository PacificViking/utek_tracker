from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

chats = []
rescue_packages = []

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
    pass

@app.route('/get_messages', methods=['GET'])
def get_messages():
    user = request.args.get('user')

    if not user:
        return jsonify({"error": "Missing user parameter"}), 400

    user_chats = [chat for chat in chats if chat['sender']['name'] == user or chat['receiver']['name'] == user]
    return jsonify({"messages": user_chats}), 200

@app.route('/update_package_status', methods=['POST'])
def update_package_status():
    data = request.json
    package_info = data.get('package_info')
    status = data.get('status')

    if not all([package_info, status]):
        return jsonify({"error": "Missing package_info or status"}), 400

    for package in rescue_packages:
        if package['package_info'] == package_info:
            package['status'] = status
            package['updated_at'] = datetime.utcnow().isoformat()
            return jsonify({"message": "Package status updated successfully", "package_info": package_info, "status": status}), 200

    return jsonify({"error": "Package not found"}), 404

@app.route('/get_package_status', methods=['GET'])
def get_package_status():
    package_info = request.args.get('package_info')

    if not package_info:
        return jsonify({"error": "Missing package_info parameter"}), 400

    for package in rescue_packages:
        if package['package_info'] == package_info:
            return jsonify({"package_info": package_info, "status": package}), 200

    return jsonify({"error": "Package not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)