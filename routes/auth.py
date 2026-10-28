"""
Routes d'authentification administrateur (/api/auth/*).
"""

from flask import Blueprint, request, jsonify
from config import ADMIN_PASSWORD, JWT_EXPIRY_HOURS
from middlewares.auth import generate_token, verify_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    if data.get("password") == ADMIN_PASSWORD:
        token = generate_token()
        return jsonify({
            "success": True,
            "token": token,
            "expires_in": f"{JWT_EXPIRY_HOURS}h",
        }), 200
    return jsonify({"error": "Mot de passe incorrect"}), 401


@auth_bp.route("/api/auth/verify", methods=["GET"])
def verify():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer ") and verify_token(auth.split(" ", 1)[1]):
        return jsonify({"valid": True}), 200
    return jsonify({"valid": False}), 401
