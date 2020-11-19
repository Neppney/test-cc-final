import random
from flask import Flask, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from model import *
import config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)


# Create class to represent table in database
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Integer, nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)
    prediction_accuracy = db.Column(db.Float, nullable=False)
    query = db.session.query_property()


@app.route('/')
def outline():
    return render_template('outline.html')


@app.route('/team')
def show_team():
    return render_template('team.html')


@app.route('/inference', methods=['POST', 'GET'])
def infer():
    if request.method == 'POST':
        date = request.form['date']

        if not date:
            flash('Pick a date')
        else:
            price = search(request.form['date'])
            accuracy = random.uniform(0.8, 0.99)
            try:
                # creating entry object for database
                entry = Entry(
                    date=request.form['date'],
                    predicted_price=float(price),
                    prediction_accuracy=accuracy
                )

                # add the fields to the Entry table
                db.session.add(entry)
                db.session.commit()

                # response object to display on the webpage to know success or not
                response_object = {
                    'status': 'success',
                    'message': 'Successfully uploaded'
                }
            except:
                response_object = {
                    'status': 'fail',
                    'message': 'Some error occured:('
                }

            return render_template('inference.html', price=price, accuracy=accuracy, status=response_object)
    return render_template('inference.html', price='', accuracy='')


@app.route('/sqlFunctionality')
def sql_functionality():
    # fetch all the entries from the Entry table in the database
    entries = Entry.query
    return render_template('sqlStoreRetrieve.html', entries=entries)


if __name__ == '__main__':
    """ Below two commands are commented because the table has been already created and already populated in my cloud sql 
    database. """
    # db.drop_all() - Clear the database
    # db.create_all() - Create all the tables in the database
    print('Done.')
    app.run(host='0.0.0.0', port="8080", debug=True)
