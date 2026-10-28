"""
Point d'entrée principal de l'API Flask du Portfolio.
Initialise l'application, configure le CORS et enregistre les routes modulaires.
"""

from flask import Flask
from flask_cors import CORS
from config import ALLOWED_ORIGINS, PORT
from routes import register_routes


def create_app() -> Flask:
    """Crée et configure l'instance de l'application Flask."""
    application = Flask(__name__)

    # Configuration CORS restreinte aux domaines autorisés
    CORS(
        application,
        resources={r"/api/*": {"origins": ALLOWED_ORIGINS}},
        supports_credentials=True,
    )

    # Enregistrement de tous les modules de routes (Blueprints)
    register_routes(application)

    return application


app = create_app()

if __name__ == "__main__":
    print(f"Serveur Flask sur http://127.0.0.1:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
