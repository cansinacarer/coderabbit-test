from flask import Flask, request, jsonify

app = Flask(__name__)

users = {
    1: {"name": "Alice", "email": "alice@example.com", "balance": 100.0},
    2: {"name": "Bob", "email": "bob@example.com", "balance": 50.0},
}


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user = users.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/users/<int:user_id>/transfer", methods=["POST"])
def transfer(user_id):
    data = request.get_json()
    recipient_id = data["recipient_id"]
    amount = data["amount"]

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
    data = request.get_json()
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
