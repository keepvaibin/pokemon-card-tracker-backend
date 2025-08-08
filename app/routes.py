from flask import Blueprint, jsonify, request
from .auth import require_auth
from .models import db, Card, Ability, Attack, Weakness, Resistance

routes_bp = Blueprint("routes", __name__)

# --- Existing routes ---
@routes_bp.route("/")
def home():
    return jsonify({"status": "ok"})

@routes_bp.route("/protected")
@require_auth
def protected():
    return jsonify({"message": f"Hello {request.user['email']}!"})


# --- Utility serializer ---
def serialize_card(card: Card):
    return {
        "id": card.id,
        "name": card.name,
        "supertype": card.supertype,
        "subtypes": card.subtypes,
        "hp": card.hp,
        "types": card.types,
        "rarity": card.rarity,
        "set": {
            "id": card.set_id,
            "name": card.set_name,
            "series": card.set_series,
            "releaseDate": card.set_release_date,
        },
        "abilities": [
            {
                "name": ability.name,
                "text": ability.text,
                "type": ability.type
            }
            for ability in card.abilities
        ],
        "attacks": [
            {
                "name": attack.name,
                "cost": attack.cost,
                "damage": attack.damage,
                "text": attack.text
            }
            for attack in card.attacks
        ],
        "weaknesses": [
            {
                "type": weakness.type,
                "value": weakness.value
            }
            for weakness in card.weaknesses
        ],
        "resistances": [
            {
                "type": resistance.type,
                "value": resistance.value
            }
            for resistance in card.resistances
        ]
    }


# --- New API endpoints ---
@routes_bp.route("/cards", methods=["GET"])
def get_all_cards():
    cards = Card.query.all()
    return jsonify([serialize_card(card) for card in cards])

@routes_bp.route("/cards/<string:card_id>", methods=["GET"])
def get_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    return jsonify(serialize_card(card))
