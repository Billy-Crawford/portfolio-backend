"""
Configuration centrale de l'application Flask.
Charge les variables d'environnement depuis le fichier .env.
"""

import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Origines autorisées pour CORS (Frontend Vercel + développement local)
ALLOWED_ORIGINS = [
    "https://obilly-portfolio.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Identifiants Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Authentification Administrateur & JWT
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

# Port du serveur
PORT = int(os.getenv("PORT", "5001"))
