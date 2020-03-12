# CS 421 Database Project
Trumark is a database system that implements a website front end to facilitate querying of the database. Queries are string based using a tag systems "inspired" (read ripped) by [scryfall](https://scryfall.com/docs/syntax).

## Todo
* update schema to reflect the intended implementation
* implement search box stump
* database implementation
* magic card data mass import

## Implementation

### Front/Back end
- python (with the [flask framework](https://palletsprojects.com/p/flask/))

### Database
- [SQLite](https://sqlite.org/index.html)

Note: SQLite database files can be interacted with via the command line ([link](https://sqlite.org/cli.html))

#### Schema
[Diagram Documentation](documentation/documentation.pdf)
![ER diagram](schema/ER_diagram.png)

Note: as the schema is updated the dot file must also be updated and compiled to reflect those changes (use the makefile).

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
- Israel **Tru**sdell
