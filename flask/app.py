import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
sys.path.insert(1, '../database/')
from create_db import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/trumark.db'
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def getQuery():
    query = request.form['query']

    # write function to split query, based on scryfall
    
    # simple tests below
    # if '!' we search for specific card by name
    # Ex: !Sol Ring
    if query[0] == '!':
        card_name = query[1:]
        results = db.session.query(Card).filter(Card.card_name == card_name)


    
    # function to run query
    #results = db.session.query(Format).all()

    return render_template('results.html', results=results)
