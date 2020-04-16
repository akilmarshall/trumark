from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Index

# import the tables
from create_db import Card, Format, Set, Contains, Limitation, Color, \
    Color_cost, Subtype, Supertype, Type, Color_identity

engine = create_engine('sqlite:///trumark.db')
Session = sessionmaker(bind=engine)
session = Session()


for card in session.query(Card.__table__).filter(Card.card_name == 'Fireball'):
    print(card)
