import re
from sqlalchemy import create_engine, MetaData, Table, Integer, Float, String, Boolean, Column, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import Index

DB_PATH = 'sqlite:///trumark.db'
#engine = create_engine(DB_PATH, echo = True)
engine = create_engine(DB_PATH)
engine.execute('pragma foreign_keys=on')  # Foreign keys are disable by default in SQLite

Base = declarative_base()


class Card(Base):
    __tablename__ = 'CARD'

    # _id = Column(Integer, autoincrement=True, primary_key=True)
    card_name = Column(String, primary_key=True, index=True)
    text = Column(String, nullable=True)
    power = Column(Integer, nullable=True)
    toughness = Column(Integer, nullable=True)
    loyalty = Column(Integer, nullable=True)

    # The following two compute columns have not been tested
    @hybrid_property
    def is_double_card_front(self):
        if 'transform' in self.text:
            return True

        return False

    @hybrid_property
    def is_double_card_back(self):
        if self.Color_cost.converted_cost == 0 and self.Type.type_ == 'creature':
            return True

        return False

    def __repr__(self):
        text = self.text
        if text is not None and len(text) > 10:
            text = f'{text[0:10]}..'
        return f'{self.__tablename__}(card_name={self.card_name}, text={text}, power={self.power}, toughness={self.toughness}, loyalty={self.loyalty})'

        
class Format(Base):
    __tablename__ = 'FORMAT'

    format_name = Column(String, primary_key=True)
    min_deck_size = Column(Integer, nullable=False)
    max_deck_size = Column(Integer, nullable=False)
    copies_allowed = Column(Integer, nullable=False)
    format_type = Column(String, nullable=False)
    multiplayer = Column(Boolean, nullable=False)

    def __repr__(self):
        return f'{self.__tablename__}(format_name={self.format_name}, min_deck_size={self.min_deck_size}, max_deck_size={self.max_deck_size}, copies_allowed={self.copies_allowed}, format_type={self.format_type}, multiplayer={self.multiplayer})'


class Set(Base):
    __tablename__ = 'SET'

    set_code = Column(String, primary_key=True)
    set_name = Column(String, nullable=False)
    release_date = Column(String, nullable=False)
    set_type = Column(String, nullable=False)

    def __repr__(self):
        return f'{self.__tablename__}(set_code={self.set_code}, set_name={self.set_name}, release_date={self.release_date}, set_type={self.set_type})'


# class Is_allowed(Base):
#     __tablename__ = 'IS_ALLOWED'

#     set_code = Column(Integer, ForeignKey('SET.set_code'), primary_key=True)
#     format_name = Column(String, ForeignKey('FORMAT.format_name'), primary_key=True)

#     Format = relationship('Format', backref='Is_allowed')
#     Set = relationship('Set', backref='Is_allowed')

#    def __repr__(self):
#        return f'{self.__name__}(set_code={self.set_code}, format_name={self.format_name})'


class Contains(Base):
    __tablename__ = 'CONTAINS'

    set_code = Column(Integer, ForeignKey('SET.set_code'), primary_key=True)
    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    rarity = Column(String, nullable=False)

    Card = relationship('Card', backref='Contains')
    Set = relationship('Set', backref='Contains')

    def __repr__(self):
        return f'{self.__name__}(set_code={self.set_code}, card_name={self.card_name}, rarity={self.rarity})'


class Limitation(Base):
    __tablename__ = 'LIMITATION'

    format_name = Column(String, ForeignKey('FORMAT.format_name'), primary_key=True)
    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    limitation_type = Column(String, nullable=False)

    Card = relationship('Card', backref='Limitation')
    Format = relationship('Format', backref='Limitation')

    def __repr__(self):
        return f'{self.__tablename__}(format_name={self.format_name}, card_name={self.card_name}, limitation_type={self.limitation_type})'


class Color(Base):
    __tablename__ = 'COLOR'

    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    color = Column(String, primary_key=True, index=True)

    Card = relationship('Card', backref='Color')

    def __repr__(self):
        return f'{self.__tablename__}(card_name={self.card_name}, color={self.color})'


class Color_cost(Base):
    __tablename__ = 'COLOR_COST'

    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    cost_string = Column(String, index=True)
    converted_cost = Column(Integer)

    Card = relationship('Card', backref='Color_cost')

    def __repr__(self):
        return f'{self.__tablename__}(card_name={self.card_name}, cost_string={self.cost_string}, converted_cost={self.converted_cost})'

  


class Subtype(Base):
    __tablename__ = 'SUBTYPE'

    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    subtype = Column(String, nullable=False, index=True)

    Card = relationship('Card', backref='Subtype')

    def __repr__(self):
        return f'{self.__tablename__}(card_name={self.card_name}, subtype={self.subtype})'

 


class Supertype(Base):
    __tablename__ = 'SUPERTYPE'

    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    supertype = Column(String, nullable=False, index=True)

    Card = relationship('Card', backref='Supertype')

    def __repr__(self):
        return f'{self.__tablename__}(card_name={self.card_name}, supertype={self.supertype})'


class Type(Base):
    __tablename__ = 'TYPE'

    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    type_ = Column(String, nullable=False, index=True)

    Card = relationship('Card', backref='Type')

    def __repr__(self):
        return f'{self.__tablename__}(card_name={self.card_name}, type_={self.type_})'



class Color_identity(Base):
    __tablename__ = 'COLOR_IDENTITY'

    card_name = Column(String, ForeignKey('CARD.card_name'), primary_key=True)
    red = Column(Boolean, nullable=False)
    blue = Column(Boolean, nullable=False)
    green = Column(Boolean, nullable=False)
    black = Column(Boolean, nullable=False)
    white = Column(Boolean, nullable=False)

    Card = relationship('Card', backref='Color_identity')

    def __repr__(self):
        return f'{self.__tablename__}(card_name={self.card_name}, red={self.red}, blue={self.blue}, green={self.green}, black={self.black}, white={self.white})'


if __name__ == '__main__':
    Base.metadata.create_all(engine)
