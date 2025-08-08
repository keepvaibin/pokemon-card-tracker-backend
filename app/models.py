from sqlalchemy import (
    Column, String, Integer, Float, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from .db import Base

class Card(Base):
    __tablename__ = "Card"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    supertype = Column(String)
    subtypes = Column(ARRAY(String))
    level = Column(String)
    hp = Column(String)
    types = Column(ARRAY(String))
    evolvesFrom = Column(String)
    evolvesTo = Column(ARRAY(String))
    rules = Column(ARRAY(String))
    flavorText = Column(String)
    artist = Column(String)
    rarity = Column(String)
    number = Column(String, nullable=False)
    nationalPokedexNumbers = Column(ARRAY(Integer))
    setId = Column(String, ForeignKey("CardSet.id"))
    retreatCost = Column(ARRAY(String))
    convertedRetreatCost = Column(Integer)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)

    abilities = relationship("Ability", back_populates="card")
    attacks = relationship("Attack", back_populates="card")
    weaknesses = relationship("Weakness", back_populates="card")
    resistances = relationship("Resistance", back_populates="card")
    legalities = relationship("CardLegalities", uselist=False, back_populates="card")
    images = relationship("CardImages", uselist=False, back_populates="card")
    cardmarket = relationship("CardMarket", uselist=False, back_populates="card")
    tcgplayer = relationship("TcgPlayer", uselist=False, back_populates="card")
    set = relationship("CardSet", back_populates="cards")

class Ability(Base):
    __tablename__ = "Ability"
    id = Column(String, primary_key=True)
    cardId = Column(String, ForeignKey("Card.id"), nullable=False)
    name = Column(String)
    text = Column(String)
    type = Column(String)

    card = relationship("Card", back_populates="abilities")

class Attack(Base):
    __tablename__ = "Attack"
    id = Column(String, primary_key=True)
    cardId = Column(String, ForeignKey("Card.id"), nullable=False)
    name = Column(String)
    cost = Column(ARRAY(String))
    convertedEnergyCost = Column(Integer)
    damage = Column(String)
    text = Column(String)

    card = relationship("Card", back_populates="attacks")

class Weakness(Base):
    __tablename__ = "Weakness"
    id = Column(String, primary_key=True)
    cardId = Column(String, ForeignKey("Card.id"))
    type = Column(String)
    value = Column(String)

    card = relationship("Card", back_populates="weaknesses")

class Resistance(Base):
    __tablename__ = "Resistance"
    id = Column(String, primary_key=True)
    cardId = Column(String, ForeignKey("Card.id"))
    type = Column(String)
    value = Column(String)

    card = relationship("Card", back_populates="resistances")

class CardLegalities(Base):
    __tablename__ = "CardLegalities"
    id = Column(String, primary_key=True)
    cardId = Column(String, ForeignKey("Card.id"), unique=True)
    unlimited = Column(String)
    standard = Column(String)
    expanded = Column(String)

    card = relationship("Card", back_populates="legalities")

class CardImages(Base):
    __tablename__ = "CardImages"
    id = Column(String, primary_key=True)
    cardId = Column(String, ForeignKey("Card.id"), unique=True)
    small = Column(String)
    large = Column(String)

    card = relationship("Card", back_populates="images")

class CardMarket(Base):
    __tablename__ = "CardMarket"
    id = Column(String, primary_key=True)
    cardId = Column(String, ForeignKey("Card.id"), unique=True)
    url = Column(String)
    updatedAt = Column(DateTime)
    averageSellPrice = Column(Float)
    lowPrice = Column(Float)
    trendPrice = Column(Float)
    germanProLow = Column(Float)
    suggestedPrice = Column(Float)
    reverseHoloSell = Column(Float)
    reverseHoloLow = Column(Float)
    reverseHoloTrend = Column(Float)
    lowPriceExPlus = Column(Float)
    avg1 = Column(Float)
    avg7 = Column(Float)
    avg30 = Column(Float)
    reverseHoloAvg1 = Column(Float)
    reverseHoloAvg7 = Column(Float)
    reverseHoloAvg30 = Column(Float)

    card = relationship("Card", back_populates="cardmarket")

class TcgPlayerPrices(Base):
    __tablename__ = "TcgPlayerPrices"
    id = Column(String, primary_key=True)
    normalLow = Column(Float)
    normalMid = Column(Float)
    normalHigh = Column(Float)
    normalMarket = Column(Float)
    normalDirectLow = Column(Float)
    holofoilLow = Column(Float)
    holofoilMid = Column(Float)
    holofoilHigh = Column(Float)
    holofoilMarket = Column(Float)
    holofoilDirectLow = Column(Float)
    reverseHolofoilLow = Column(Float)
    reverseHolofoilMid = Column(Float)
    reverseHolofoilHigh = Column(Float)
    reverseHolofoilMarket = Column(Float)
    reverseHolofoilDirectLow = Column(Float)

    tcgplayer = relationship("TcgPlayer", back_populates="prices", uselist=False)

class TcgPlayer(Base):
    __tablename__ = "TcgPlayer"
    id = Column(String, primary_key=True)
    cardId = Column(String, ForeignKey("Card.id"), unique=True)
    url = Column(String)
    updatedAt = Column(DateTime)
    pricesId = Column(String, ForeignKey("TcgPlayerPrices.id"), unique=True)

    card = relationship("Card", back_populates="tcgplayer")
    prices = relationship("TcgPlayerPrices", back_populates="tcgplayer")

class CardSet(Base):
    __tablename__ = "CardSet"
    id = Column(String, primary_key=True)
    name = Column(String)
    series = Column(String)
    printedTotal = Column(Integer)
    total = Column(Integer)
    ptcgoCode = Column(String)
    releaseDate = Column(DateTime)
    updatedAt = Column(DateTime)
    symbol = Column(String)
    logo = Column(String)

    cards = relationship("Card", back_populates="set")
    legalities = relationship("SetLegalities", uselist=False, back_populates="set")

class SetLegalities(Base):
    __tablename__ = "SetLegalities"
    id = Column(String, primary_key=True)
    setId = Column(String, ForeignKey("CardSet.id"), unique=True)
    unlimited = Column(String)
    standard = Column(String)
    expanded = Column(String)

    set = relationship("CardSet", back_populates="legalities")

class ImportMetadata(Base):
    __tablename__ = "ImportMetadata"
    id = Column(String, primary_key=True)
    totalCount = Column(Integer)
    importedAt = Column(DateTime)
    isFullImport = Column(Integer)  # Boolean stored as integer or use Boolean type if supported
