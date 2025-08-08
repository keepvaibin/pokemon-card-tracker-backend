import os
from flask import request, jsonify, g
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def verify_google_token(token):
    try:
        id_info = id_token.verify_oauth2_token(
            token, grequests.Request(), GOOGLE_CLIENT_ID
        )
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            print("❌ Invalid issuer:", id_info['iss'])
            return None
        return id_info
    except ValueError as e:
        print("❌ Token verification error:", e)
        return None

def require_auth(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth_header.split(" ")[1]
        user_info = verify_google_token(token)
        if not user_info:
            return jsonify({"error": "Invalid token"}), 401

        g.user = user_info
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
