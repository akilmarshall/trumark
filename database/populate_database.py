'''
This script populates the database with all magic card printings from mtgjson.com
'''
from os.path import isfile
import json
import requests
from create_db import Format, Set, Contains, Limitation, Color, Color_cost, Card, Type, Subtype, Supertype, Color_identity, Is_allowed
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
        format_type='constructed',
        multiplayer=True)

    session.add(brawl)

    commander = Format(
        format_name='commander',
        min_deck_size=100,
        max_deck_size=100,
        copies_allowed=1,
        format_type='constructed',
        multiplayer=False)

    session.add(commander)

    duel = Format(
        format_name='duel',
        min_deck_size=100,
        max_deck_size=100,
        copies_allowed=1,
        format_type='constructed',
        multiplayer=False)

    session.add(duel)

    frontier = Format(
        format_name='frontier',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.add(frontier)

    legacy = Format(
        format_name='legacy',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.add(legacy)

    modern = Format(
        format_name='modern',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.add(modern)

    pauper = Format(
        format_name='pauper',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.add(pauper)

    penny = Format(
        format_name='penny',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.add(penny)

    pioneer = Format(
        format_name='pioneer',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.add(pioneer)

    standard = Format(
        format_name='standard',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.add(standard)

    vintage = Format(
        format_name='vintage',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.add(vintage)
    session.commit()


def populate_rest(file='AllPrintings.json'):
    '''
    All tables except FORMAT is populated by the information in file
    file must be the json from mtgjson.com/file/allprintings

    Sets are the top level object in this json file
    This function iterates over the sets and first creates a corresponding entity
    in the SET table and then creates related entities in the all other tables
    of the database (excluding FORMAT and IS_ALLOWED which is populated by the populate_format function).
    '''
    session = Session()

    with open(file) as f:
        card_sets = json.load(f)
        for s in card_sets:
            set_code = card_sets[s].get('code')  # will need this again a foreign key

            # A Set entity to be added to the SET table
            set_entity = Set(
                set_code=set_code,
                set_name=card_sets[s].get('name'),
                release_date=card_sets[s].get('releaseDate'),
                set_type=card_sets[s].get('type'))

            session.add(set_entity)

            for card in card_sets[s]['cards']:
                card_name = card.get('name')  # will need this again as a foreign key

                # A Card entity to be added to the CARD table
                card_entity = Card(
                    card_name=card_name,
                    text=card.get('text'),
                    power=card.get('power'),
                    toughness=card.get('toughness'),
                    loyalty=card.get('loyalty'))

                session.merge(card_entity)  # merge updates a duplicate entry if it exists

                # A Contains entity to be added to the CONTAINS table
                contains_entity = Contains(
                    set_code=set_code,
                    card_name=card_name,
                    rarity=card.get('rarity'))

                session.merge(contains_entity)

                for format_ in card['legalities']:
                    legality = card.get('legalities')[format_]
                    limitation_type = str()
                    if legality == 'Legal':
                        limitation_type = 'none'
                    else:
                        limitation_type = legality.lower()

                    # A Limitation entity to be added to the LIMITATION table
                    limitation_entity = Limitation(
                        format_name=format_,
                        card_name=card_name,
                        limitation_type=limitation_type)

                    session.merge(limitation_entity)

                # dictionary to map the color letters to their corresponding word
                color_format = {'U': 'blue', 'R': 'red', 'G': 'green', 'B': 'black', 'W': 'white'}
                # Color entity to be added to the Color table
                if card['colors'] == []:
                    color_entity = Color(
                        card_name=card_name,
                        color='colorless')
                else:
                    for color in card['colors']:
                        color_entity = Color(
                            card_name=card_name,
                            color=color_format[color])

                session.merge(color_entity)

                def format_cost_string(manacost):
                    if manacost:
                        return manacost.replace('{', '').replace('}', '')
                    else:
                        return ''
                # Color_cost entity to be added to the Color_cost table
                cost_string = card.get('manaCost')
                color_cost_entity = Color_cost(
                    card_name=card_name,
                    cost_string=format_cost_string(cost_string))

                session.merge(color_cost_entity)

                supertype = card.get('supertype')
                if supertype:
                    for s_type in supertype:
                        # Supertype entity to be added to the Supertype table
                        supertype_entity = Supertype(
                            card_name=card_name,
                            supertype=s_type)

                        session.merge(supertype_entity)

                subtype = card.get('subtype')
                if subtype:
                    for s_type in subtype:
                        # Subtype entity to be added to the Subtype table
                        subtype_entity = Subtype(
                            card_name=card_name,
                            subtype=s_type)

                        session.merge(subtype_entity)

                types = card.get('types')
                type_ = set(types)
                if supertype:
                    type_.difference_update(supertype)

                if subtype:
                    type_.difference_update(subtype)

                # Type entity to be added to the Type table
                for t in type_:
                    type_entity = Type(
                        card_name=card_name,
                        type_=t)

                    session.merge(type_entity)

                color_id = dict()  # dict to keep track of the color identity flags
                for color in ['R', 'G', 'U', 'B', 'W']:
                    color_id[color] = False  # default alignment is false
                    if color in card['colorIdentity']:
                        color_id[color] = True

                # Color_identity entity to be added to the Color_identity table
                color_identity_entity = Color_identity(
                    card_name=card_name,
                    red=color_id['R'],
                    blue=color_id['U'],
                    green=color_id['G'],
                    black=color_id['B'],
                    white=color_id['W'])

                session.merge(color_identity_entity)

            session.commit()


if __name__ == '__main__':
    all_printings = 'https://www.mtgjson.com/files/AllPrintings.json'
    file = 'AllPrintings.json'

    if not isfile(file):
        print(f'{file} not found, downloading from {all_printings}')
        print('This will take a few minutes.')
        get_all_cards(all_printings, file)

    populate_format()  # populate the FORMAT table
    populate_rest()  # populate the rest of the tables
