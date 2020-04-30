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
    d = {'Card':Card, 'Color_cost': Color_cost, 'Type': Type}
    query = request.form['query']
    clauses = query.split(',')
    print(clauses)
    domain, case = clauses[0].split(':')
    domain = domain.lower().strip()
    case = case.lower().strip()
    print(domain, case)
    results = db.session

    results = single_query(results, domain, case)

    for clause in clauses[1:]:
        domain, case = clause.split(':')
        domain = domain.lower().strip()
        case = case.lower().strip()
        results = append_query(results, domain, case)

    return render_template('results.html', results=results)


def single_query(results, domain, case):

    # search for case in text 
    if domain == 'o':
        results = results.query(Card).filter(Card.text.like(f'%{case}%'))

    if domain == 'mana':  # maybe make this 'cost'
        results = results.query(Color_cost).filter(Color_cost.cost_string == case.upper())

    return results

def append_query(results, domain, case):
    # search for case in text 

    if domain == 'o':
        results = results.join(Card).filter(Card.text.like(f'%{case}%'))

    if domain == 'mana':  # maybe make this 'cost'
        results = results.join(Color_cost).filter(Color_cost.cost_string == case.upper())

    return results
