"""
Gestion des tokens JWT et décorateur de protection des routes administrateur.
"""

import datetime
from functools import wraps
import jwt
from flask import request, jsonify
from config import JWT_SECRET, JWT_EXPIRY_HOURS


def generate_token() -> str:
    """Génère un token JWT signé valable pendant JWT_EXPIRY_HOURS heures."""
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": "admin",
        "iat": now,
        "exp": now + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> bool:
    """Vérifie la validité et la date d'expiration d'un token JWT."""
    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return True
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return False


def require_admin(f):
    """Décorateur protégeant les routes réservées à l'administrateur (POST, PUT, DELETE)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Token manquant"}), 401
        token = auth.split(" ", 1)[1]
        if not verify_token(token):
            return jsonify({"error": "Token invalide ou expire"}), 401
        return f(*args, **kwargs)

    return decorated
