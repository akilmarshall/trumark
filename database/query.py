from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# import the tables
from create_db import Card, Format, Set, Contains, Limitation, Color, \
    Color_cost, Subtype, Supertype, Type, Color_identity


# TODO: (super low priority) gather all similar engine/session calls
# to one file, base.py then can import from that.
engine = create_engine('sqlite:///trumark.db')
Session = sessionmaker(bind=engine)
session = Session()


formats = session.query(Format).all()
for fmt in formats:
    print(fmt)

#from sqlalchemy.schema import CreateTable
print(dir(Card))
print(Card.metadata)

