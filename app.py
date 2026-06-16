from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

users = {
    1: {"name": "Alice", "email": "alice@example.com", "balance": 100.0},
    2: {"name": "Bob", "email": "bob@example.com", "balance": 50.0},
}
users_lock = threading.Lock()


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = users.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/users/<int:user_id>/transfer", methods=["POST"])
def transfer(user_id):
    # Authentication check - verify caller is authorized to debit from user_id
    # In a real application, extract authenticated_user_id from session/token
    # For now, we'll use a request header as a placeholder
    authenticated_user_id = request.headers.get("X-User-ID")
    if authenticated_user_id is None:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        authenticated_user_id = int(authenticated_user_id)
    except ValueError:
        return jsonify({"error": "Unauthorized"}), 401

    if authenticated_user_id != user_id:
        return jsonify({"error": "Forbidden - cannot transfer from another user's account"}), 403

    # Input validation
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Bad Request - payload must be a JSON object"}), 400

    if "recipient_id" not in data:
        return jsonify({"error": "Bad Request - recipient_id is required"}), 400
    if "amount" not in data:
        return jsonify({"error": "Bad Request - amount is required"}), 400

    try:
        recipient_id = int(data["recipient_id"])
    except (ValueError, TypeError):
        return jsonify({"error": "Bad Request - recipient_id must be an integer"}), 400

    try:
        amount = float(data["amount"])
        if amount < 0:
            return jsonify({"error": "Bad Request - amount must be non-negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Bad Request - amount must be numeric"}), 400

    with users_lock:
        sender = users.get(user_id)
        recipient = users.get(recipient_id)

        if sender is None or recipient is None:
            return jsonify({"error": "User not found"}), 404

        if sender["balance"] < amount:
            return jsonify({"error": "Insufficient funds"}), 400

        sender["balance"] -= amount
        recipient["balance"] += amount

        return jsonify({"status": "ok", "sender_balance": sender["balance"]})


@app.route("/users", methods=["POST"])
def create_user():
    # Input validation
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Bad Request - payload must be a JSON object"}), 400

    if "name" not in data:
        return jsonify({"error": "Bad Request - name is required"}), 400
    if "email" not in data:
        return jsonify({"error": "Bad Request - email is required"}), 400

    with users_lock:
        new_id = max(users.keys()) + 1
        users[new_id] = {
            "name": data["name"],
            "email": data["email"],
            "balance": 0.0,
        }
        return jsonify({"id": new_id}), 201


@app.route("/users/<int:user_id>/discount", methods=["GET"])
def get_discount(user_id):
    user = users.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    balance = user["balance"]
    if balance > 100.0:
        discount = 0.10
    elif balance > 50.0:
        discount = 0.05
    else:
        discount = 0.0

    return jsonify({"discount": discount})


if __name__ == "__main__":
    app.run(debug=False)
