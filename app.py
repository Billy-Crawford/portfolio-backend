"""
Point d'entrée principal de l'API Flask du Portfolio.
Initialise l'application, configure le CORS, enregistre les routes modulaires
et démarre le maintien en éveil automatique de Supabase.
"""

from flask import Flask
from flask_cors import CORS
from config import ALLOWED_ORIGINS, PORT
from routes import register_routes
from middlewares.keep_alive import start_supabase_keep_alive


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

    # Démarrage du thread de maintien en éveil de Supabase
    start_supabase_keep_alive()

    return application


app = create_app()

if __name__ == "__main__":
    print(f"Serveur Flask sur http://127.0.0.1:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
