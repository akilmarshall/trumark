from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap


app = Flask(__name__)
# app.config['SECRET_KEY'] = 'sometimes I wander in the mid morning.'
Bootstrap(app)

def decode(user_query:str):
    # function from a user_query to function calls that pull data from the database 
    pass


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        # will print the user input to terminal
        print(request.form['query'])

        return render_template('index.html')
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
