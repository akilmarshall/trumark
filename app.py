#from flask import Flask, render_template
from flask_bootstrap import Bootstrap


import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
sys.path.insert(1, 'database/')
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
app.config['SECRET_KEY'] = 'sometimes I wander in the mid morning.'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/trumark.db'
db = SQLAlchemy(app)


def parseRelation(case):
    '''helper function to parse a relational case (in query) such as <10
    case: string, e.g., '<9, >10, == 3, <=9
    returns: (string, string)'''
    # get the number to eval at by removing non digits
    val = re.sub(r'[^\d]', '', case)
    # get the operator by removing digits
    oper = d[re.sub(r'[\d]', '', case)]
    return oper, val

@app.route('/')
def index():
    return render_template('index.html')

#@app.route('/')
#def root():
#    return render_template('index.html')

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
    results = [str(x).replace("'","").replace('(','').replace(')','') for x in results]
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
    if domain == 'name':  # maybe make this 'name'
        # Search for keyword in CARD JOIN COLOR_COST
        # Wanted to see casting cost with card, always.
        results = session.query(Card.card_name)\
                .add_column(Color_cost.cost_string)\
                .join(Color_cost)\
                .filter(Card.card_name.like(f'%{case}%'))

    # Search for keyword in CARD text, e.g., 'o:island walk'
    elif domain == 'text': 
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

    # search for a supertype, e.g., 'super:Legendary'
    elif domain == 'super':
        results = session.query(Supertype.supertype)\
                .add_column(Supertype.card_name)\
                .filter(Supertype.supertype.like(f'%{case}%'))

    # search for cards that have one or more colors, e.g., 'color:rg' for red AND green cards
    elif domain == 'color': # maybe make this 'color'
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
        # get the relational data, e.g, <, 10
        oper, num = parseRelation(case)
        num = int(num)
        
        results = session.query(Color_cost.converted_cost)\
                .add_column(Color_cost.cost_string)\
                .add_column(Color_cost.card_name)\
                .filter(oper(Color_cost.converted_cost, num))

    elif domain == 'type':
        results = session.query(Type.type_)\
                .add_column(Type.card_name)\
                .filter(Type.type_.like(f'%{case}%'))

    elif domain == 'in':
        results = session.query(Contains.card_name)\
                .add_column(Contains.set_code)\
                .filter(Contains.card_name.like(f'%{case}%'))

    elif domain == 'set':
        '''get all card in a set given the set code.
        Note: this cannot follow another query in a query chain'''
        # special case where we want to get all the sets
        if case == 'all':
            results = session.query(Set.set_code)\
                    .add_column(Set.set_name)\
                    .add_column(Set.release_date)

        # special case when dealing with release dates
        elif case[0] in ['<','>','<=','>=','==']:
            # set:<2020-05-22
            oper = re.sub(r'[^<>=]', '', case)
            oper = d[oper]
            date = re.sub(r'[<>=]', '', case)
            print(f'[{oper}] [{date}]')

            results = session.query(Set.release_date)\
                    .add_column(Set.release_date)\
                    .add_column(Set.set_name)\
                    .filter(oper(Set.release_date, date)).order_by(Set.release_date.desc())
        else:
            results = session.query(Set.set_code)\
                    .join(Contains)\
                    .add_column(Set.set_name)\
                    .add_column(Contains.card_name)\
                    .filter(Contains.set_code.like(f'%{case}%'))


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

        if domain == 'name':
            if 'CARD' in sql_statement:
                # CARD table already joined, just filter
                results = results.filter(Card.card_name.like(f'%{case}%'))
            else:
                results = results.join(Card).filter(Card.card_name.like(f'%{case}%'))

        elif domain == 'text':
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
            # With two tables there are four conditions we need to check for before joining.
            if 'CARD' in sql_statement and 'SUBTYPE' in sql_statement:
                results = results.filter(Subtype.subtype.like(f'%{case}%'))
            if 'CARD' in sql_statement and 'SUBTYPE' not in sql_statement:
                results = results.join(Subtype).add_column(Subtype.subtype).filter(Subtype.subtype.like(f'%{case}%'))
            if 'CARD' not in sql_statement and 'SUBTYPE' in sql_statement:
                results = results.join(Card).filter(Subtype.subtype.like(f'%{case}%'))
            if 'CARD' not in sql_statement and 'SUBTYPE' not in sql_statement:
                results = results.join(Card).join(Subtype).add_column(Subtype.subtype).filter(Subtype.subtype.like(f'%{case}%'))


        elif domain == 'super':
            # With two tables there are four conditions we need to check for before joining.
            if 'CARD' in sql_statement and 'SUPERTYPE' in sql_statement:
                results = results.filter(Supertype.supertype.like(f'%{case}%'))
            if 'CARD' in sql_statement and 'SUPERTYPE' not in sql_statement:
                results = results.join(Supertype).add_column(Supertype.supertype).filter(Supertype.supertype.like(f'%{case}%'))
            if 'CARD' not in sql_statement and 'SUPERTYPE' in sql_statement:
                results = results.join(Card).filter(Supertype.supertype.like(f'%{case}%'))
            if 'CARD' not in sql_statement and 'SUPERTYPE' not in sql_statement:
                results = results.join(Card).join(Supertype).add_column(Supertype.supertype).filter(Supertype.supertype.like(f'%{case}%'))



        elif domain == 'type':
            # With two tables there are four conditions we need to check for before joining.
            if 'CARD' in sql_statement and '"TYPE"' in sql_statement:
                print(1)
                results = results.add_entity(Type).filter(Type.type_.like(f'%{case}%'))
            if 'CARD' in sql_statement and '"TYPE"' not in sql_statement:
                print(2)
                results = results.add_entity(Type).join(Type).filter(Type.type_.like(f'%{case}%'))
            if 'CARD' not in sql_statement and '"TYPE"' in sql_statement:
                print(3)
                results = results.add_entity(Type).join(Card).filter(Type.type_.like(f'%{case}%'))
            if 'CARD' not in sql_statement and '"TYPE"' not in sql_statement:
                print(4)
                results = results.add_entity(Type).join(Card).join(Type).filter(Type.type_.like(f'%{case}%'))
        

        # all cards with combined casting cost
        elif domain == 'cost':
            # get the relational data, e.g, <, 10
            oper, num = parseRelation(case)
            num = int(num)

            # auto join intermediate table if needed, otherwise join only whats needed
            if 'COLOR_COST' not in sql_statement:
                try:
                    results = results.join(Color_cost)
                except:
                    results = results.join(Card).join(Color_cost)
                
            if 'cost_string' not in sql_statement and 'converted_cost' not in sql_statement:
                results = results.add_column(Color_cost.converted_cost)\
                        .add_column(Color_cost.cost_string)\
                        .filter(oper(Color_cost.converted_cost, num))
            if 'cost_string' not in sql_statement and 'converted_cost' in sql_statement:
                results = results.add_column(Color_cost.cost_string)\
                        .filter(oper(Color_cost.converted_cost, num))
            if 'cost_string' in sql_statement and 'converted_cost' not in sql_statement:
                results = results.add_column(Color_cost.converted_cost)\
                        .filter(oper(Color_cost.converted_cost, num))
            if 'cost_string' in sql_statement and 'converted_cost' in sql_statement:
                results = results.filter(oper(Color_cost.converted_cost, num))

        elif domain == 'in':
            if 'CONTAINS' not in sql_statement:
                results = results.join(Contains.card_name)\
                        .add_column(Contains.set_code)\
                        .filter(Contains.card_name.like(f'%{case}%'))
            else:
                results = results.filter(Contains.card_name.like(f'%{case}%'))


    except Exception as e:
        print(e)
        return ['Invalid search request, please try again']

    return results



#if __name__ == '__main__':
#    app.run(debug=True)
