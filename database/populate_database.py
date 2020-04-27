'''
This script populates the database with all magic card printings from mtgjson.com
'''
from os.path import isfile
import json
import requests
from create_db import Format, Set, Contains, Limitation, Color_cost, Card, Type, Subtype, Supertype, Color_identity
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DB_PATH = 'sqlite:///trumark.db'
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)


def get_all_cards(source_url, file_name):
    '''
    function to download a json file located at source_url to a localfile, file_name
    '''

    response = requests.get(source_url)
    all_cards = json.loads(response.text)
    with open(file_name, 'w') as file:
        json.dump(all_cards, file, indent=1)


def populate_format(session):
    '''
    certain information about formats is not stored in the json card data.
    min_deck_size, max_deck, and copies_allowed are specified manually by
    this function
    '''

    brawl = Format(
        format_name='brawl',
        min_deck_size=60,
        max_deck_size=60,
        copies_allowed=1,
        format_type='constructed',
        multiplayer=True)

    session.merge(brawl)

    commander = Format(
        format_name='commander',
        min_deck_size=100,
        max_deck_size=100,
        copies_allowed=1,
        format_type='constructed',
        multiplayer=False)

    session.merge(commander)

    duel = Format(
        format_name='duel',
        min_deck_size=100,
        max_deck_size=100,
        copies_allowed=1,
        format_type='constructed',
        multiplayer=False)

    session.merge(duel)

    frontier = Format(
        format_name='frontier',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.merge(frontier)

    legacy = Format(
        format_name='legacy',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.merge(legacy)

    modern = Format(
        format_name='modern',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.merge(modern)

    pauper = Format(
        format_name='pauper',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.merge(pauper)

    penny = Format(
        format_name='penny',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.merge(penny)

    pioneer = Format(
        format_name='pioneer',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.merge(pioneer)

    standard = Format(
        format_name='standard',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.merge(standard)

    vintage = Format(
        format_name='vintage',
        min_deck_size=60,
        max_deck_size=-1,
        copies_allowed=4,
        format_type='constructed',
        multiplayer=False)

    session.merge(vintage)


def populate_set(session, set_):
    '''
    helper function of populate_rest
    given a dictionary containing a card_set populate the Set table
    see https://www.mtgjson.com/structures/set/ for details about the dictionary
    '''

    # A Set entity to be added to the SET table
    set_entity = Set(
        set_code=set_.get('code'),
        set_name=set_.get('name'),
        release_date=set_.get('releaseDate'),
        set_type=set_.get('type'))

    session.merge(set_entity)


def populate_card(session, card):
    '''
    helper function of populate_rest
    given a dictionary containing a card populate the Card table
    see https://www.mtgjson.com/structures/card/ for details about the dictionary
    '''

    # A Card entity to be added to the CARD table
    card_entity = Card(
        card_name=card.get('name'),
        text=card.get('text'),
        power=card.get('power'),
        toughness=card.get('toughness'),
        loyalty=card.get('loyalty'))

    session.merge(card_entity)  # merge updates a duplicate entry if it exists


def populate_contains(session, card, set_code):
    '''
    helper function of populate_rest
    given a dictionary containing a card and a set_code populate the Set table
    see https://www.mtgjson.com/structures/card/ for details about the dictionary
    '''
    # A Contains entity to be added to the CONTAINS table
    contains_entity = Contains(
        set_code=set_code,
        card_name=card.get('name'),
        rarity=card.get('rarity'))

    session.merge(contains_entity)


def populate_limitations(session, card):
    '''
    helper function of populate_rest
    given a dictionary containing a card populate the Limitation table
    see https://www.mtgjson.com/structures/card/ for details about the dictionary
    '''

    # iterate over formats
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
            card_name=card.get('name'),
            limitation_type=limitation_type)

        session.merge(limitation_entity)


def populate_color(session, card):
    '''
    helper function of populate_rest
    given a dictionary containing a card populate the Color table
    see https://www.mtgjson.com/structures/card/ for details about the dictionary
    '''

    # Color entity to be added to the Color table
    if card['colors'] == []:
        color_entity = Color(
            card_name=card.get('name'),
            color='C')

        session.merge(color_entity)
    else:
        for color in card['colors']:
            color_entity = Color(
                card_name=card.get('name'),
                color=color)

            session.merge(color_entity)


def populate_color_cost(session, card):
    '''
    helper function of populate_rest
    given a dictionary containing a card populate the Color_cost table
    see https://www.mtgjson.com/structures/card/ for details about the dictionary
    '''
    color_cost_entity = Color_cost(
        card_name=card.get('name'),
        cost_string=card.get('manaCost'),
        converted_cost=int(card.get('convertedManaCost')))

    session.merge(color_cost_entity)


def populate_supertype(session, card):
    '''
    helper function of populate_rest
    given a dictionary containing a card populate the supertype table
    see https://www.mtgjson.com/structures/card/ for details about the dictionary
    '''

    supertype = card.get('supertypes')
    if supertype:
        for s_type in supertype:
            # Supertype entity to be added to the Supertype table
            supertype_entity = Supertype(
                card_name=card.get('name'),
                supertype=s_type)

            session.merge(supertype_entity)


def populate_type(session, card):
    '''
    helper function of populate_rest
    given a dictionary containing a card populate the type table
    see https://www.mtgjson.com/structures/card/ for details about the dictionary
    '''
    types = card.get('types')
    supertype = card.get('supertypes')
    subtype = card.get('subtypes')
    type_ = set(types)
    if supertype:
        type_.difference_update(supertype)

    if subtype:
        type_.difference_update(subtype)

    # Type entity to be added to the Type table
    for t in type_:
        type_entity = Type(
            card_name=card.get('name'),
            type_=t.lower())

        session.merge(type_entity)


def populate_subtype(session, card):
    '''
    helper function of populate_rest
    given a dictionary containing a card populate the subtype table
    see https://www.mtgjson.com/structures/card/ for details about the dictionary
    '''

    subtype = card.get('subtypes')
    if subtype:
        for s_type in subtype:
            # Subtype entity to be added to the Subtype table
            subtype_entity = Subtype(
                card_name=card.get('name'),
                subtype=s_type)

            session.merge(subtype_entity)


def populate_color_identity(session, card):
    '''
    helper function of populate_rest
    given a dictionary containing a card populate the Color_identity table
    see https://www.mtgjson.com/structures/card/ for details about the dictionary
    '''

    color_id = dict()  # dict to keep track of the color identity flags
    for color in ['R', 'G', 'U', 'B', 'W']:
        color_id[color] = False  # default alignment is false
        if color in card['colorIdentity']:
            color_id[color] = True

    # Color_identity entity to be added to the Color_identity table
    color_identity_entity = Color_identity(
        card_name=card.get('name'),
        red=color_id['R'],
        blue=color_id['U'],
        green=color_id['G'],
        black=color_id['B'],
        white=color_id['W'])

    session.merge(color_identity_entity)


def populate_rest(session, file='AllPrintings.json'):
    '''
    All tables except FORMAT is populated by the information in file
    file must be the json from mtgjson.com/file/allprintings

    Sets are the top level object in this json file
    This function iterates over the sets and first creates a corresponding entity
    in the SET table and then creates related entities in the all other tables
    of the database (excluding FORMAT and IS_ALLOWED which is populated by the populate_format function).
    '''

    with open(file) as f:
        card_sets = json.load(f)
        for s in card_sets:
            set_code = card_sets[s].get('code')  # will need this again a foreign key

            populate_set(session, card_sets[s])

            for card in card_sets[s]['cards']:
                populate_card(session, card)
                populate_contains(session, card, set_code)
                populate_limitations(session, card)
                populate_color(session, card)
                populate_color_cost(session, card)
                populate_supertype(session, card)
                populate_type(session, card)
                populate_subtype(session, card)
                populate_color_identity(session, card)


if __name__ == '__main__':
    all_printings = 'https://www.mtgjson.com/files/AllPrintings.json'
    file = 'AllPrintings.json'

    if not isfile(file):
        print(f'{file} not found, downloading from {all_printings}')
        print('This will take a few minutes.')
        get_all_cards(all_printings, file)

    session = Session()

    populate_format(session)  # populate the FORMAT table
    populate_rest(session)  # populate the rest of the tables


    session.commit()
