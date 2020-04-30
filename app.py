from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = 'sqlite:///database/trumark.db'
engine = create_engine(DB_PATH, echo=False)
Session = sessionmaker(bind=engine)


app = Flask(__name__)
Bootstrap(app)  # enables the bootstrap CSS

# a dict associating  query identifiers with tables
# this also acts as a rudimentary filter since a user input query cannot be proccessed
# if the identifier they specify is not in this table
table = {'name': 'Card', 'text': 'Card', 'power': 'Card', 'toughness': 'Card',
         'loyalty': 'Card'}

# maybe this function will return some kind of dict that
# has all the query information nicely parsed
def decode(user_query:str):
    x = user_query.split(':')[1:]
    Card = dict()
    for blob in x:  # a blob is a query identifier paired with it's arguments
        blob = blob.split()
        identifier = blob[0]
        arguments = blob[1:]
        if table[identifier] == 'Card':
            Card[identifier] = arguments

    return {'Card': Card}


def query(info:dict):
    # TODO dynamic quries using the SQLAlchemy ORM
    '''
    session = Session()
    a = session.query(Card)
    for item in info['Card']:
    '''


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        print(decode(request.form['query']))

        return render_template('index.html')
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
