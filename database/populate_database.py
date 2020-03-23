'''
This script populates the database with all magic card printings from mtgjson.com
'''
from os.path import isfile
import json
import requests
from create_db import Format
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DB_PATH = 'sqlite:///trumark.db'
engine = create_engine(DB_PATH, echo=True)
Session = sessionmaker(bind=engine)


def get_all_cards(source_url, file_name):
    '''
    function to download a json file located at source_url to a localfile, file_name
    '''
    response = requests.get(source_url)
    all_cards = json.loads(response.text)
    with open(file_name, 'w') as file:
        json.dump(all_cards, file, indent=1)


def populate_format():
    '''
    certain information about formats is not stored in the json card data.
    min_deck_size, max_deck, and copies_allowed are specified manually by
    this function
    '''
    session = Session()

    brawl = Format(
        format_name='brawl',
        min_deck_size=60,
        max_deck_size=60,
        copies_allowed=1,
        format_type='constructed')
    session.add(brawl)

    commander = Format(
        format_name='commander',
        min_deck_size=60,
        max_deck_size=60,
        copies_allowed=1)
    session.add(commander)

    session.commit()


if __name__ == '__main__':
    all_printings = 'https://www.mtgjson.com/files/AllPrintings.json'
    file = 'AllPrintings.json'

    if not isfile(file):
        print(f'{file} not found, downloading from {all_printings}')
        print('This will take a few minutes.')
        get_all_cards(all_printings, file)

    populate_format()  # populate the FORMAT table


