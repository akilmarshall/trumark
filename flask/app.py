import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
sys.path.insert(1, '../database/')
from create_db import *
from create_db import Card

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/trumark.db'
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def getQuery():
    d = {'Card':Card, 'Color_cost': Color_cost, 'Type': Type, '!': Card}
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
        print(f'[{domain}:{case}]')
        results = append_query(results, domain, case)

    return render_template('results.html', results=results)


def single_query(results, domain, case):

    # search for case in text 
    if domain == '!':  # maybe make this 'name'
        results = results.query(Card).filter(Card.card_name.like(f'%{case}%'))

    elif domain == 'o':
        results = results.query(Card).filter(Card.text.like(f'%{case}%'))

    elif domain == 'mana':  # maybe make this 'cost'
        results = results.query(Color_cost).filter(Color_cost.cost_string == case.upper())
    
    elif domain == 't': # maybe make this 'subtype',
        results = results.query(Card, Subtype).join(Subtype).filter(Subtype.subtype.like(f'%{case}%'))

    return results

def append_query(results, domain, case):
    # search for case in text 
    try:
        if domain == '!':
            if 'CARD' in str(results):
                results = results.filter(Card.card_name.like(f'%{case}%'))
            else:
                results = results.join(Card).filter(Card.card_name.like(f'%{case}%'))

        elif domain == 'o':
            if 'CARD' in str(results):
                results = results.filter(Card.text.like(f'%{case}%'))
            else:
                results = results.join(Card).filter(Card.text.like(f'%{case}%'))

        elif domain == 'mana':  # maybe make this 'cost'
            if 'COLOR_COST' in str(results):
                results = results.filter(Color_cost.cost_string == case.upper())
            else:
                results = results.join(Color_cost).filter(Color_cost.cost_string == case.upper())

        elif domain == 't': # maybe make this 'subtype',
            if 'SUBTYPE' in str(results) and 'CARD' in str(results):
                results = results.filter(Subtype.subtype.like(f'%{case}%'))
            if 'CARD' in str(results) and 'SUBTYPE' not in str(results):
                results = results.join(Subtype).filter(Subtype.subtype.like(f'%{case}%'))
            
            # other cases here

            if 'CARD' not in str(results) and 'SUBTYPE' not in str(results):
                results = results.join(Card, Subtype).join(Subtype).filter(Subtype.subtype.like(f'%{case}%'))

    except Exception as e:
        print(e)
        return ['Invalid search request, please try again']

    return results
