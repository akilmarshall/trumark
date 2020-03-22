from sqlalchemy import create_engine, MetaData, Table, Integer, Float, String, Boolean, Column, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

DB_PATH = 'sqlite:///trumark.db'
engine = create_engine(DB_PATH, echo = True)
engine.execute('pragma foreign_keys=on')  # Foreign keys are disable by default in SQLite

Base = declarative_base()

class Card(Base):
    __tablename__ = 'CARD'

    card_name = Column(String, primary_key=True)
    text = Column(String, nullable=True)
    type = Column(String, nullable=False)
    supertype = Column(String, nullable=False)
    power = Column(Integer, nullable=True)
    toughness = Column(Integer, nullable=True)
    loyalty = Column(Integer, nullable=True)


class Format(Base):
    __tablename__ = 'FORMAT'

    format_name = Column(String, primary_key=True)
    deck_size = Column(Integer, nullable=False)
    num_players = Column(Integer, nullable=False)
    copies_allowed = Column(Integer, nullable=False)


class Set(Base):
    __tablename__ = 'SET'

    set_num = Column(Integer, primary_key=True)
    set_name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)


class Is_allowed(Base):
    __tablename__ = 'IS_ALLOWED'

    set_num = Column(Integer, ForeignKey('SET.set_num'), primary_key=True)
    format_name = Column(String, ForeignKey('FORMAT.format_name'), primary_key=True)

    Format = relationship('Format', backref='Is_allowed')
    Set = relationship('Set', backref='Is_allowed')


class Contains(Base):
    __tablename__ = 'CONTAINS'

    set_num = Column(Integer, ForeignKey('SET.set_num'), primary_key=True)
    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    rarity = Column(String, nullable=False)

    Card = relationship('Card', backref='Contains')
    Set = relationship('Set', backref='Contains')


class Limitation(Base):
    __tablename__ = 'LIMITATION'

    format_name = Column(String, ForeignKey('FORMAT.format_name'), primary_key=True)
    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    limitation_type = Column(String, nullable=False)

    Card = relationship('Card', backref='Limitation')
    Format = relationship('Format', backref='Limitation')


class Color(Base):
    __tablename__ = 'COLOR'

    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    color = Column(String)

    Card = relationship('Card', backref='Color')


class Color_cost(Base):
    __tablename__ = 'COLOR_COST'

    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    cost_string = Column(String)

    Card = relationship('Card', backref='Color_cost')


class Double_card(Base):
    __tablename__ = 'DOUBLE_CARD'

    side_a = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    side_b = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    set_num = Column(Integer, ForeignKey('SET.set_num'), primary_key=True)

    Card_a = relationship('Card', backref='Double_card')
    Card_b = relationship('Card', backref='Double_card')
    Set = relationship('Set', backref='Double_card')


class Subtype(Base):
    __tablename__ = 'SUBTYPE'

    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    subtype = Column(String, nullable=False)

    Card = relationship('Card', backref='Subtype')


class Color_identity(Base):
    __tablename__ = 'COLOR_IDENTITY'

    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    red = Column(Boolean, nullable=False)
    blue = Column(Boolean, nullable=False)
    green = Column(Boolean, nullable=False)
    black = Column(Boolean, nullable=False)
    white = Column(Boolean, nullable=False)
    colorless = Column(Boolean, nullable=False)
    converted_cost = Column(Integer, nullable=False)

    Card = relationship('Card', backref='Subtype')


if __name__ == '__main__':
    Base.metadata.create_all(engine)
