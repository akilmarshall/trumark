import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
sys.path.insert(1, '../database/')
from create_db import *
import operator
import re

# global operator dict
d = {'<': operator.lt,
     '>': operator.gt,
     '<=': operator.le,
     '>=': operator.ge,
     '==': operator.eq}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/trumark.db'
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def getQuery():
    # get the string from the webpage
    query = request.form['query']
    # each clause is an independent database interaction
    # query = 'o:text, mana:{1}{U}' -> [o:text, mana:{1}{U}] 
    clauses = query.split(',')

    # preprocess user input for database interaction
    # 'o:text' -> [o, text]
    domain, case = clauses[0].split(':')
    domain = domain.lower().strip()
    case = case.lower().strip()
    print(f'[{domain}:{case}]')

    results = db.session
    # create base case, for first clause.
    results = single_query(results, domain, case)

    # if there are more clauses, then we keep on chaining them together
    # using the append_query function
    for clause in clauses[1:]:
        domain, case = clause.split(':')
        domain = domain.lower().strip()
        case = case.lower().strip()
        results = append_query(results, domain, case)

    # return the results to html
    return render_template('results.html', results=results)


def single_query(session, domain, case):
    '''process the query and return the results of the generated sql statement.
    session: database session, e.g., db.session, note: db = SQLAlchemy(app)
    domain: the space that the query will search.
    case: the item that we search for within the domain
    returns: sqlalchemy object full of table objects (an iterable).

    purpose: given preprocessed user input (via webpage) build a query that returns a query
    that can be used as a base for further table joins or filters.'''

    # the default tables that we display from, we are always interested in casting cost.
    if domain == '!':  # maybe make this 'name'
        # Search for keyword in CARD JOIN COLOR_COST
        # Wanted to see casting cost with card, always.
        results = session.query(Card.card_name)\
                .add_column(Color_cost.cost_string)\
                .join(Color_cost)\
                .filter(Card.card_name.like(f'%{case}%'))

    # Search for keyword in CARD text, e.g., 'o:island walk'
    elif domain == 'o': 
        results = session.query(Card.text)\
                .add_column(Card.card_name)\
                .filter(Card.text.like(f'%{case}%'))

    # search for a specific mana cost, e.g., 'mana:{U}{U}'
    elif domain == 'mana': 
        # cost string must include brackets, e.g., {1}{G}{G}. 
        # upper() needed because all queries are lower().
        results = session.query(Color_cost.cost_string)\
                .add_column(Color_cost.card_name)\
                .filter(Color_cost.cost_string == case.upper())
    
    # search for a subtype, e.g., 'sub:Merfolk'
    elif domain == 'sub':
        results = session.query(Subtype.subtype)\
                .add_column(Subtype.card_name)\
                .filter(Subtype.subtype.like(f'%{case}%'))

    # search for cards that have one or more colors, e.g., 'c:rg' for red AND green cards
    elif domain == 'c': # maybe make this 'color'
        col_d = {'r': 0, 'w': 0, 'g': 0, 'b':0, 'u': 0}
        colors = list(case)
        # set dict to true for color requested
        for col in colors:
            if col in col_d.keys():
                col_d[col] = 1
        results = session.query(Color_identity).filter(Color_identity.black == col_d['b'])
        results = results.filter(Color_identity.blue == col_d['u'])
        results = results.filter(Color_identity.green == col_d['g'])
        results = results.filter(Color_identity.white == col_d['w'])
        results = results.filter(Color_identity.red == col_d['r'])

    # all cards with combined casting cost
    elif domain == 'cost':
        num = int(re.sub(r'[^\d]', '', case))
        oper = re.sub(r'[\d]', '', case)
        
        results = session.query(Color_cost.converted_cost)\
                .add_column(Color_cost.cost_string)\
                .add_column(Color_cost.card_name)\
                .filter(d[oper](Color_cost.converted_cost, num))

    


    # probably add elif statements at least for type, limitation, format, and set


    return results

def append_query(results, domain, case):
    '''used to chain mulitple joins or filters from a base query created by single_query.
    results: sqlalchemy object that has some list attributes, typcially the output form 
    single_query
    domain: the space that the query will search.
    case: the item that we search for within the domain

    purpose: needed a function that appends tables nicely.  .query methods are not used
    in this function, only .join and .filter methods.  Also this function creates calls
    that do not have duplicate table joins which cause ambigous table join errors.
    NOTE: domain changes to singe_query need to be refected in append_query
    NOTE: all queries should already query tables CARD and COLOR_COST'''
    try:
        # tailored commands to join tables necessary for the chained queries 
        # without naming conflicts due to duplicate table joins.
        # Note, that some commands also have add_entity so the user can view the
        # results specific to that query if it was not previously added.
        
        # [SELECT "COLOR_COST".card_name AS "COLOR_COST_card_name", ...]
        sql_statement = str(results)

        if domain == '!':
            if 'CARD' in sql_statement:
                # CARD table already joined, just filter
                results = results.filter(Card.card_name.like(f'%{case}%'))
            else:
                results = results.join(Card).filter(Card.card_name.like(f'%{case}%'))

        elif domain == 'o':
            if 'CARD' in sql_statement:
                results = results.filter(Card.text.like(f'%{case}%'))
            else:
                results = results.join(Card).filter(Card.text.like(f'%{case}%'))

        elif domain == 'mana':  # maybe make this 'cost'
            if 'COLOR_COST' in sql_statement:
                results = results.filter(Color_cost.cost_string == case.upper())
            else:
                results = results.join(Color_cost).filter(Color_cost.cost_string == case.upper())
        
        elif domain == 'sub':
            print('in sub')
            # With two tables there are four conditions we need to check for before joining.
            if 'CARD' in sql_statement and 'SUBTYPE' in sql_statement:
                results = results.add_entity(Subtype).filter(Subtype.subtype.like(f'%{case}%'))
            if 'CARD' in sql_statement and 'SUBTYPE' not in sql_statement:
                results = results.add_entity(Subtype).join(Subtype).filter(Subtype.subtype.like(f'%{case}%'))
            if 'CARD' not in sql_statement and 'SUBTYPE' in sql_statement:
                results = results.add_entity(Subtype).join(Card).filter(Subtype.subtype.like(f'%{case}%'))
            if 'CARD' not in sql_statement and 'SUBTYPE' not in sql_statement:
                results = results.add_entity(Subtype).join(Card).join(Subtype).filter(Subtype.subtype.like(f'%{case}%'))

        # all cards with combined casting cost
        elif domain == 'cost':
            # get the number to eval at by removing non digits
            num = int(re.sub(r'[^\d]', '', case))
            # get the operator by removing digits
            oper = re.sub(r'[\d]', '', case)

            if 'COLOR_COST' not in sql_statement:
                try:
                    results = results.join(Color_cost)
                except:
                    results = results.join(Card).join(Color_cost)
                
            if 'cost_string' not in sql_statement and 'converted_cost' not in sql_statement:
                results = results.add_column(Color_cost.converted_cost)\
                        .add_column(Color_cost.cost_string)\
                        .filter(d[oper](Color_cost.converted_cost, num))
            if 'cost_string' not in sql_statement and 'converted_cost' in sql_statement:
                results = results.add_column(Color_cost.cost_string)\
                        .filter(d[oper](Color_cost.converted_cost, num))
            if 'cost_string' in sql_statement and 'converted_cost' not in sql_statement:
                results = results.add_column(Color_cost.converted_cost)\
                        .filter(d[oper](Color_cost.converted_cost, num))
            if 'cost_string' in sql_statement and 'converted_cost' in sql_statement:
                results = results.filter(d[oper](Color_cost.converted_cost, num))


    except Exception as e:
        print(e)
        return ['Invalid search request, please try again']

    return results
