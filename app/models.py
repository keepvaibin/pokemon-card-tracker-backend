# app/models.py
from .db import db
from sqlalchemy.dialects.postgresql import ARRAY

class Card(db.Model):
    __tablename__ = "Card"
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    supertype = db.Column(db.String)
    subtypes = db.Column(ARRAY(db.String))
    level = db.Column(db.String)
    hp = db.Column(db.String)
    types = db.Column(ARRAY(db.String))
    evolvesFrom = db.Column(db.String)
    evolvesTo = db.Column(ARRAY(db.String))
    rules = db.Column(ARRAY(db.String))
    flavorText = db.Column(db.String)
    artist = db.Column(db.String)
    rarity = db.Column(db.String)
    number = db.Column(db.String, nullable=False)
    nationalPokedexNumbers = db.Column(ARRAY(db.Integer))
    setId = db.Column(db.String, db.ForeignKey("CardSet.id"))
    retreatCost = db.Column(ARRAY(db.String))
    convertedRetreatCost = db.Column(db.Integer)
    createdAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)

    abilities = db.relationship("Ability", back_populates="card")
    attacks = db.relationship("Attack", back_populates="card")
    weaknesses = db.relationship("Weakness", back_populates="card")
    resistances = db.relationship("Resistance", back_populates="card")
    legalities = db.relationship("CardLegalities", uselist=False, back_populates="card")
    images = db.relationship("CardImages", uselist=False, back_populates="card")
    cardmarket = db.relationship("CardMarket", uselist=False, back_populates="card")
    tcgplayer = db.relationship("TcgPlayer", uselist=False, back_populates="card")
    set = db.relationship("CardSet", back_populates="cards")


class Ability(db.Model):
    __tablename__ = "Ability"
    id = db.Column(db.String, primary_key=True)
    cardId = db.Column(db.String, db.ForeignKey("Card.id"), nullable=False)
    name = db.Column(db.String)
    text = db.Column(db.String)
    type = db.Column(db.String)

    card = db.relationship("Card", back_populates="abilities")


class Attack(db.Model):
    __tablename__ = "Attack"
    id = db.Column(db.String, primary_key=True)
    cardId = db.Column(db.String, db.ForeignKey("Card.id"), nullable=False)
    name = db.Column(db.String)
    cost = db.Column(ARRAY(db.String))
    convertedEnergyCost = db.Column(db.Integer)
    damage = db.Column(db.String)
    text = db.Column(db.String)

    card = db.relationship("Card", back_populates="attacks")


class Weakness(db.Model):
    __tablename__ = "Weakness"
    id = db.Column(db.String, primary_key=True)
    cardId = db.Column(db.String, db.ForeignKey("Card.id"))
    type = db.Column(db.String)
    value = db.Column(db.String)

    card = db.relationship("Card", back_populates="weaknesses")


class Resistance(db.Model):
    __tablename__ = "Resistance"
    id = db.Column(db.String, primary_key=True)
    cardId = db.Column(db.String, db.ForeignKey("Card.id"))
    type = db.Column(db.String)
    value = db.Column(db.String)

    card = db.relationship("Card", back_populates="resistances")


class CardLegalities(db.Model):
    __tablename__ = "CardLegalities"
    id = db.Column(db.String, primary_key=True)
    cardId = db.Column(db.String, db.ForeignKey("Card.id"), unique=True)
    unlimited = db.Column(db.String)
    standard = db.Column(db.String)
    expanded = db.Column(db.String)

    card = db.relationship("Card", back_populates="legalities")


class CardImages(db.Model):
    __tablename__ = "CardImages"
    id = db.Column(db.String, primary_key=True)
    cardId = db.Column(db.String, db.ForeignKey("Card.id"), unique=True)
    small = db.Column(db.String)
    large = db.Column(db.String)

    card = db.relationship("Card", back_populates="images")


class CardMarket(db.Model):
    __tablename__ = "CardMarket"
    id = db.Column(db.String, primary_key=True)
    cardId = db.Column(db.String, db.ForeignKey("Card.id"), unique=True)
    url = db.Column(db.String)
    updatedAt = db.Column(db.DateTime)
    averageSellPrice = db.Column(db.Float)
    lowPrice = db.Column(db.Float)
    trendPrice = db.Column(db.Float)
    germanProLow = db.Column(db.Float)
    suggestedPrice = db.Column(db.Float)
    reverseHoloSell = db.Column(db.Float)
    reverseHoloLow = db.Column(db.Float)
    reverseHoloTrend = db.Column(db.Float)
    lowPriceExPlus = db.Column(db.Float)
    avg1 = db.Column(db.Float)
    avg7 = db.Column(db.Float)
    avg30 = db.Column(db.Float)
    reverseHoloAvg1 = db.Column(db.Float)
    reverseHoloAvg7 = db.Column(db.Float)
    reverseHoloAvg30 = db.Column(db.Float)

    card = db.relationship("Card", back_populates="cardmarket")


class TcgPlayerPrices(db.Model):
    __tablename__ = "TcgPlayerPrices"
    id = db.Column(db.String, primary_key=True)
    normalLow = db.Column(db.Float)
    normalMid = db.Column(db.Float)
    normalHigh = db.Column(db.Float)
    normalMarket = db.Column(db.Float)
    normalDirectLow = db.Column(db.Float)
    holofoilLow = db.Column(db.Float)
    holofoilMid = db.Column(db.Float)
    holofoilHigh = db.Column(db.Float)
    holofoilMarket = db.Column(db.Float)
    holofoilDirectLow = db.Column(db.Float)
    reverseHolofoilLow = db.Column(db.Float)
    reverseHolofoilMid = db.Column(db.Float)
    reverseHolofoilHigh = db.Column(db.Float)
    reverseHolofoilMarket = db.Column(db.Float)
    reverseHolofoilDirectLow = db.Column(db.Float)

    tcgplayer = db.relationship("TcgPlayer", back_populates="prices", uselist=False)


class TcgPlayer(db.Model):
    __tablename__ = "TcgPlayer"
    id = db.Column(db.String, primary_key=True)
    cardId = db.Column(db.String, db.ForeignKey("Card.id"), unique=True)
    url = db.Column(db.String)
    updatedAt = db.Column(db.DateTime)
    pricesId = db.Column(db.String, db.ForeignKey("TcgPlayerPrices.id"), unique=True)

    card = db.relationship("Card", back_populates="tcgplayer")
    prices = db.relationship("TcgPlayerPrices", back_populates="tcgplayer")


class CardSet(db.Model):
    __tablename__ = "CardSet"
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    series = db.Column(db.String)
    printedTotal = db.Column(db.Integer)
    total = db.Column(db.Integer)
    ptcgoCode = db.Column(db.String)
    releaseDate = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)
    symbol = db.Column(db.String)
    logo = db.Column(db.String)

    cards = db.relationship("Card", back_populates="set")
    legalities = db.relationship("SetLegalities", uselist=False, back_populates="set")


class SetLegalities(db.Model):
    __tablename__ = "SetLegalities"
    id = db.Column(db.String, primary_key=True)
    setId = db.Column(db.String, db.ForeignKey("CardSet.id"), unique=True)
    unlimited = db.Column(db.String)
    standard = db.Column(db.String)
    expanded = db.Column(db.String)

    set = db.relationship("CardSet", back_populates="legalities")


class ImportMetadata(db.Model):
    __tablename__ = "ImportMetadata"
    id = db.Column(db.String, primary_key=True)
    totalCount = db.Column(db.Integer)
    importedAt = db.Column(db.DateTime)
    isFullImport = db.Column(db.Integer)  # Boolean stored as integer or use Boolean type if supported
