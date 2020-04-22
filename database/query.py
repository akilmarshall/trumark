from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

# import the tables
from create_db import Card, Format, Set, Contains, Limitation, Color, \
    Color_cost, Subtype, Supertype, Type, Color_identity

engine = create_engine('sqlite:///trumark.db')
Session = sessionmaker(bind=engine)
session = Session()


# generalize and turn these into functions
for card in session.query(Card).filter(Card.card_name == 'Fireball'):
    print(card)
print('\n\n\n\n')

for card in session.query(Card).filter(Card.text.like('%ball%')):
    print(card)
print('\n\n\n\n')

# the object returned is based on the order of the join
card_join_limitation = session.query(Card).join(Limitation)
limitation_join_card = session.query(Limitation).join(Card)
for card in card_join_limitation.filter(Limitation.limitation_type == 'restricted'):
    print(card)
print('\n\n\n\n')
for limit in limitation_join_card.filter(Limitation.limitation_type == 'restricted'):
    print(limit)

#for card in session.query(Card).filter(Card






