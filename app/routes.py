from flask import Blueprint, jsonify, request
from sqlalchemy import and_
from .models import (
    Card, Ability, Attack, Weakness, Resistance,
    CardLegalities, CardImages, CardMarket,
    TcgPlayer, TcgPlayerPrices, CardSet, SetLegalities
)
from .db import db
from .auth import require_auth

bp = Blueprint("routes", __name__)

def serialize_card_full(card: Card):
    """Serialize a card with all related data (matching model.py exactly)."""
    return {
        "id": card.id,
        "name": card.name,
        "supertype": card.supertype,
        "subtypes": card.subtypes or [],
        "level": card.level,
        "hp": card.hp,
        "types": card.types or [],
        "evolvesFrom": card.evolvesFrom,
        "evolvesTo": card.evolvesTo or [],
        "rules": card.rules or [],
        "flavorText": card.flavorText,
        "artist": card.artist,
        "rarity": card.rarity,
        "number": card.number,
        "nationalPokedexNumbers": card.nationalPokedexNumbers or [],
        "retreatCost": card.retreatCost or [],
        "convertedRetreatCost": card.convertedRetreatCost,
        "createdAt": card.createdAt.isoformat() if card.createdAt else None,
        "updatedAt": card.updatedAt.isoformat() if card.updatedAt else None,

        # --- Set ---
        "set": {
            "id": card.set.id,
            "name": card.set.name,
            "series": card.set.series,
            "printedTotal": card.set.printedTotal,
            "total": card.set.total,
            "ptcgoCode": card.set.ptcgoCode,
            "releaseDate": card.set.releaseDate.isoformat() if card.set.releaseDate else None,
            "updatedAt": card.set.updatedAt.isoformat() if card.set.updatedAt else None,
            "symbol": card.set.symbol,
            "logo": card.set.logo,
            "legalities": {
                "unlimited": card.set.legalities.unlimited if card.set.legalities else None,
                "standard": card.set.legalities.standard if card.set.legalities else None,
                "expanded": card.set.legalities.expanded if card.set.legalities else None
            } if card.set.legalities else None
        } if card.set else None,

        # --- Abilities ---
        "abilities": [
            {"id": a.id, "name": a.name, "text": a.text, "type": a.type}
            for a in card.abilities
        ],

        # --- Attacks ---
        "attacks": [
            {
                "id": atk.id,
                "name": atk.name,
                "cost": atk.cost or [],
                "convertedEnergyCost": atk.convertedEnergyCost,
                "damage": atk.damage,
                "text": atk.text
            }
            for atk in card.attacks
        ],

        # --- Weaknesses ---
        "weaknesses": [
            {"id": w.id, "type": w.type, "value": w.value}
            for w in card.weaknesses
        ],

        # --- Resistances ---
        "resistances": [
            {"id": r.id, "type": r.type, "value": r.value}
            for r in card.resistances
        ],

        # --- Legalities ---
        "legalities": {
            "unlimited": card.legalities.unlimited if card.legalities else None,
            "standard": card.legalities.standard if card.legalities else None,
            "expanded": card.legalities.expanded if card.legalities else None
        } if card.legalities else None,

        # --- Images ---
        "images": {
            "small": card.images.small if card.images else None,
            "large": card.images.large if card.images else None
        } if card.images else None,

        # --- CardMarket (full) ---
        "cardmarket": {
            "url": card.cardmarket.url if card.cardmarket else None,
            "updatedAt": card.cardmarket.updatedAt.isoformat() if card.cardmarket and card.cardmarket.updatedAt else None,
            "averageSellPrice": card.cardmarket.averageSellPrice if card.cardmarket else None,
            "lowPrice": card.cardmarket.lowPrice if card.cardmarket else None,
            "trendPrice": card.cardmarket.trendPrice if card.cardmarket else None,
            "germanProLow": card.cardmarket.germanProLow if card.cardmarket else None,
            "suggestedPrice": card.cardmarket.suggestedPrice if card.cardmarket else None,
            "reverseHoloSell": card.cardmarket.reverseHoloSell if card.cardmarket else None,
            "reverseHoloLow": card.cardmarket.reverseHoloLow if card.cardmarket else None,
            "reverseHoloTrend": card.cardmarket.reverseHoloTrend if card.cardmarket else None,
            "lowPriceExPlus": card.cardmarket.lowPriceExPlus if card.cardmarket else None,
            "avg1": card.cardmarket.avg1 if card.cardmarket else None,
            "avg7": card.cardmarket.avg7 if card.cardmarket else None,
            "avg30": card.cardmarket.avg30 if card.cardmarket else None,
            "reverseHoloAvg1": card.cardmarket.reverseHoloAvg1 if card.cardmarket else None,
            "reverseHoloAvg7": card.cardmarket.reverseHoloAvg7 if card.cardmarket else None,
            "reverseHoloAvg30": card.cardmarket.reverseHoloAvg30 if card.cardmarket else None,
        } if card.cardmarket else None,

        # --- TCGPlayer (full with exact model.py fields) ---
        "tcgplayer": {
            "url": card.tcgplayer.url if card.tcgplayer else None,
            "updatedAt": card.tcgplayer.updatedAt.isoformat() if card.tcgplayer and card.tcgplayer.updatedAt else None,
            "prices": {
                "normalLow": card.tcgplayer.prices.normalLow if card.tcgplayer and card.tcgplayer.prices else None,
                "normalMid": card.tcgplayer.prices.normalMid if card.tcgplayer and card.tcgplayer.prices else None,
                "normalHigh": card.tcgplayer.prices.normalHigh if card.tcgplayer and card.tcgplayer.prices else None,
                "normalMarket": card.tcgplayer.prices.normalMarket if card.tcgplayer and card.tcgplayer.prices else None,
                "normalDirectLow": card.tcgplayer.prices.normalDirectLow if card.tcgplayer and card.tcgplayer.prices else None,
                "holofoilLow": card.tcgplayer.prices.holofoilLow if card.tcgplayer and card.tcgplayer.prices else None,
                "holofoilMid": card.tcgplayer.prices.holofoilMid if card.tcgplayer and card.tcgplayer.prices else None,
                "holofoilHigh": card.tcgplayer.prices.holofoilHigh if card.tcgplayer and card.tcgplayer.prices else None,
                "holofoilMarket": card.tcgplayer.prices.holofoilMarket if card.tcgplayer and card.tcgplayer.prices else None,
                "holofoilDirectLow": card.tcgplayer.prices.holofoilDirectLow if card.tcgplayer and card.tcgplayer.prices else None,
                "reverseHolofoilLow": card.tcgplayer.prices.reverseHolofoilLow if card.tcgplayer and card.tcgplayer.prices else None,
                "reverseHolofoilMid": card.tcgplayer.prices.reverseHolofoilMid if card.tcgplayer and card.tcgplayer.prices else None,
                "reverseHolofoilHigh": card.tcgplayer.prices.reverseHolofoilHigh if card.tcgplayer and card.tcgplayer.prices else None,
                "reverseHolofoilMarket": card.tcgplayer.prices.reverseHolofoilMarket if card.tcgplayer and card.tcgplayer.prices else None,
                "reverseHolofoilDirectLow": card.tcgplayer.prices.reverseHolofoilDirectLow if card.tcgplayer and card.tcgplayer.prices else None
            } if card.tcgplayer and card.tcgplayer.prices else None
        } if card.tcgplayer else None
    }


def serialize_card_basic(card: Card):
    """Smaller version for list views with extra filterable/searchable fields and images."""
    return {
        "id": card.id,
        "name": card.name,
        "supertype": card.supertype,
        "subtypes": card.subtypes or [],
        "level": card.level,
        "hp": card.hp,
        "types": card.types or [],
        "rarity": card.rarity,
        "artist": card.artist,
        "number": card.number,
        "nationalPokedexNumbers": card.nationalPokedexNumbers or [],
        "retreatCost": card.retreatCost or [],
        "createdAt": card.createdAt.isoformat() if card.createdAt else None,

        # Set info (minimal)
        "set": {
            "id": card.set.id if card.set else None,
            "name": card.set.name if card.set else None,
            "series": card.set.series if card.set else None
        } if card.set else None,

        # Market snapshot
        "market": {
            "averageSellPrice": card.cardmarket.averageSellPrice if card.cardmarket else None,
            "trendPrice": card.cardmarket.trendPrice if card.cardmarket else None,
            "lowPrice": card.cardmarket.lowPrice if card.cardmarket else None
        } if card.cardmarket else None,

        # TCGPlayer quick prices
        "tcgplayerPrices": {
            "normalMarket": card.tcgplayer.prices.normalMarket if card.tcgplayer and card.tcgplayer.prices else None,
            "holofoilMarket": card.tcgplayer.prices.holofoilMarket if card.tcgplayer and card.tcgplayer.prices else None,
            "reverseHolofoilMarket": card.tcgplayer.prices.reverseHolofoilMarket if card.tcgplayer and card.tcgplayer.prices else None
        } if card.tcgplayer and card.tcgplayer.prices else None,

        # Images
        "images": {
            "small": card.images.small if card.images else None,
            "large": card.images.large if card.images else None
        } if card.images else None
    }

@bp.route("/cards/bulk", methods=["POST"])
@require_auth
def get_cards_bulk():
    """Fetch multiple cards by IDs and return full details."""
    data = request.get_json()

    if not data or "ids" not in data or not isinstance(data["ids"], list):
        return jsonify({"error": "Request must include 'ids' as a list"}), 400

    ids = [str(i) for i in data["ids"] if isinstance(i, str) and i.strip()]
    if not ids:
        return jsonify({"error": "No valid IDs provided"}), 400

    cards = Card.query.filter(Card.id.in_(ids)).all()

    return jsonify({
        "count": len(cards),
        "cards": [serialize_card_full(card) for card in cards]
    })


# --- Routes ---
@bp.route("/cards", methods=["GET"])
@require_auth
def get_cards():
    # Pagination params
    try:
        page = int(request.args.get("page", 1))
        page_size = min(int(request.args.get("page_size", 15)), 100)
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    # Allowed direct equality filters
    allowed_filters = {
        "id": Card.id,
        "name": Card.name,
        "supertype": Card.supertype,
        "rarity": Card.rarity,
        "hp": Card.hp,
        "level": Card.level,
        "number": Card.number,
        "setId": Card.setId,
        "artist": Card.artist,
    }

    # Allowed numeric comparison filters (suffix _gte/_lte/_gt/_lt)
    allowed_numeric_filters = {
        "hp": Card.hp,
        "averageSellPrice": CardMarket.averageSellPrice,
        "trendPrice": CardMarket.trendPrice,
        "lowPrice": CardMarket.lowPrice,
        "normalMarket": TcgPlayerPrices.normalMarket,
        "holofoilMarket": TcgPlayerPrices.holofoilMarket,
        "reverseHolofoilMarket": TcgPlayerPrices.reverseHolofoilMarket
    }

    filters = []

    for key, value in request.args.items():
        if key in ("page", "page_size"):
            continue

        # Direct match filters
        if key in allowed_filters:
            filters.append(allowed_filters[key] == value)
            continue

        # Numeric comparison filters
        for suffix, op in [("_gte", ">="), ("_lte", "<="), ("_gt", ">"), ("_lt", "<")]:
            if key.endswith(suffix):
                base_key = key[:-len(suffix)]
                if base_key in allowed_numeric_filters:
                    column = allowed_numeric_filters[base_key]
                    try:
                        num_value = float(value)
                    except ValueError:
                        return jsonify({"error": f"Invalid numeric value for {key}"}), 400
                    if op == ">=":
                        filters.append(column >= num_value)
                    elif op == "<=":
                        filters.append(column <= num_value)
                    elif op == ">":
                        filters.append(column > num_value)
                    elif op == "<":
                        filters.append(column < num_value)
                break

    # Apply filters
    query = Card.query
    if filters:
        query = query.join(CardMarket, isouter=True).join(TcgPlayer, isouter=True).join(TcgPlayerPrices, isouter=True)
        query = query.filter(and_(*filters))

    # Pagination
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    total_pages = (pagination.total + page_size - 1) // page_size

    return jsonify({
        "page": pagination.page,
        "page_size": pagination.per_page,
        "total": pagination.total,
        "total_pages": total_pages,
        "cards": [serialize_card_basic(card) for card in pagination.items]
    })


@bp.route("/cards/filters", methods=["GET"])
@require_auth
def get_card_filters():
    # Aggregates for numeric ranges
    from sqlalchemy import func

    # Numeric ranges from Card table
    hp_min, hp_max = db.session.query(func.min(Card.hp), func.max(Card.hp)).first()
    level_min, level_max = db.session.query(func.min(Card.level), func.max(Card.level)).first()
    number_min, number_max = db.session.query(func.min(Card.number), func.max(Card.number)).first()

    # Numeric ranges from CardMarket
    avg_sell_min, avg_sell_max = db.session.query(
        func.min(CardMarket.averageSellPrice), func.max(CardMarket.averageSellPrice)
    ).first()
    trend_min, trend_max = db.session.query(
        func.min(CardMarket.trendPrice), func.max(CardMarket.trendPrice)
    ).first()
    low_min, low_max = db.session.query(
        func.min(CardMarket.lowPrice), func.max(CardMarket.lowPrice)
    ).first()

    # Numeric ranges from TcgPlayerPrices
    tcg_normal_low_min, tcg_normal_low_max = db.session.query(
        func.min(TcgPlayerPrices.normalLow), func.max(TcgPlayerPrices.normalLow)
    ).first()
    tcg_holofoil_low_min, tcg_holofoil_low_max = db.session.query(
        func.min(TcgPlayerPrices.holofoilLow), func.max(TcgPlayerPrices.holofoilLow)
    ).first()
    tcg_reverse_holofoil_low_min, tcg_reverse_holofoil_low_max = db.session.query(
        func.min(TcgPlayerPrices.reverseHolofoilLow), func.max(TcgPlayerPrices.reverseHolofoilLow)
    ).first()

    # Distinct categorical values
    artists = [a[0] for a in db.session.query(Card.artist).distinct().order_by(Card.artist) if a[0]]
    rarities = [r[0] for r in db.session.query(Card.rarity).distinct().order_by(Card.rarity) if r[0]]
    supertypes = [s[0] for s in db.session.query(Card.supertype).distinct().order_by(Card.supertype) if s[0]]
    types = sorted({t for sublist in db.session.query(Card.types).distinct() for t in (sublist[0] or [])})
    sets = [ {"id": s.id, "name": s.name} for s in db.session.query(CardSet.id, CardSet.name).distinct() ]

    return jsonify({
        "ranges": {
            "hp": {"min": hp_min, "max": hp_max},
            "level": {"min": level_min, "max": level_max},
            "number": {"min": number_min, "max": number_max},
            "averageSellPrice": {"min": avg_sell_min, "max": avg_sell_max},
            "trendPrice": {"min": trend_min, "max": trend_max},
            "lowPrice": {"min": low_min, "max": low_max},
            "tcgplayer": {
                "normalLow": {"min": tcg_normal_low_min, "max": tcg_normal_low_max},
                "holofoilLow": {"min": tcg_holofoil_low_min, "max": tcg_holofoil_low_max},
                "reverseHolofoilLow": {"min": tcg_reverse_holofoil_low_min, "max": tcg_reverse_holofoil_low_max},
            }
        },
        "categories": {
            "artists": artists,
            "rarities": rarities,
            "supertypes": supertypes,
            "types": types,
            "sets": sets
        }
    })



@bp.route("/cards/<string:card_id>", methods=["GET"])
@require_auth
def get_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    return jsonify(serialize_card_full(card))
