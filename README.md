# CS 421 Database Project
Trumark is a database system that implements a website front end to facilitate querying of the database. Queries are string based using a tag systems "inspired" by [scryfall](https://scryfall.com/docs/syntax).

## Todo
* implement search box stump
* database implementation
* magic card data mass import

## Implementation

### Front/Back end
- python (with the [flask framework](https://palletsprojects.com/p/flask/))

### Database
- [SQLite](https://sqlite.org/index.html)

#### Schema
![ER diagram](schema/ER_diagram.png)

Note: as the schema is updated the dot file must also be updated and compiled to reflect those changes.

## Dependencies
- python 3.3+
- python-flask
- python-sqlalchemy
- python-flask-bootstrap
- python-flask-wtf
- python-flask-wtforms
- SQLite

## Developed by:
- Akil **Mar**shall
- John **K**uroda
- Israel **Tru**esdale
