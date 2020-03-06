from sqlalchemy import create_engine, MetaData, Table, Integer, Float, String, Boolean, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

DB_PATH = 'sqlite:///trumark.db'
engine = create_engine(DB_PATH, echo = True)

Base = declarative_base()

class Set(Base):
    __tablename__ = 'SET'
    set_num = Column(Integer, primary_key=True)
    set_name = Column(String)
    year = Column(Integer)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
