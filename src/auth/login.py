from flask import Blueprint, request, jsonify

bp = Blueprint("login", __name__)

@bp.route("/login", methods=["POST"])
def login_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    return jsonify({"message": f"Logged in as {username}"})
