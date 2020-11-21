import random
import logging
from flask import Flask, request, render_template, flash, abort, Response
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from model import *
from config import *


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
# db = SQLAlchemy(app)

logger = logging.getLogger()


def init_connection_engine():
    db_config = {
        # [START cloud_sql_mysql_sqlalchemy_limit]
        # Pool size is the maximum number of permanent connections to keep.
        "pool_size": 5,
        # Temporarily exceeds the set pool_size if no connections are available.
        "max_overflow": 2,
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # [END cloud_sql_mysql_sqlalchemy_limit]
        # [START cloud_sql_mysql_sqlalchemy_backoff]
        # SQLAlchemy automatically uses delays between failed connection attempts,
        # but provides no arguments for configuration.
        # [END cloud_sql_mysql_sqlalchemy_backoff]
        # [START cloud_sql_mysql_sqlalchemy_timeout]
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        "pool_timeout": 30,  # 30 seconds
        # [END cloud_sql_mysql_sqlalchemy_timeout]
        # [START cloud_sql_mysql_sqlalchemy_lifetime]
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # reestablished
        "pool_recycle": 1800,  # 30 minutes
        # [END cloud_sql_mysql_sqlalchemy_lifetime]
    }

    if os.environ.get("DB_HOST"):
        return init_tcp_connection_engine(db_config)
    else:
        return init_unix_connection_engine(db_config)

    # return init_tcp_connection_engine(db_config)
    # return init_unix_connection_engine(db_config)


def init_tcp_connection_engine(db_config):
    # [START cloud_sql_mysql_sqlalchemy_create_tcp]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_host = os.environ["DB_HOST"]
    # db_user = 'root'
    # db_pass = 'team11DataBases'
    # db_name = 'cc_final_database'
    # db_host = '127.0.0.1'
    # db_port = 3306

    # Extract host and port from db_host
    host_args = db_host.split(":")
    db_hostname, db_port = host_args[0], int(host_args[1])

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            host=db_host,  # e.g. "127.0.0.1"
            port=db_port,  # e.g. 3306
            database=db_name,  # e.g. "my-database-name"
        ),
        # ... Specify additional properties here.
        # [END cloud_sql_mysql_sqlalchemy_create_tcp]
        **db_config
        # [START cloud_sql_mysql_sqlalchemy_create_tcp]
    )
    # [END cloud_sql_mysql_sqlalchemy_create_tcp]

    return pool


def init_unix_connection_engine(db_config):
    # [START cloud_sql_mysql_sqlalchemy_create_socket]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    print("Using: {} | {} | {}".format(db_user, db_pass, db_name))
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    cloud_sql_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            database=db_name,  # e.g. "my-database-name"
            query={
                "unix_socket": "{}/{}".format(
                    db_socket_dir,  # e.g. "/cloudsql"
                    cloud_sql_connection_name)  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
            }
        ),
        # ... Specify additional properties here.

        # [END cloud_sql_mysql_sqlalchemy_create_socket]
        **db_config
        # [START cloud_sql_mysql_sqlalchemy_create_socket]
    )
    # [END cloud_sql_mysql_sqlalchemy_create_socket]

    return pool


# The SQLAlchemy engine will help manage interactions, including automatically
# managing a pool of connections to your database
db = init_connection_engine()


@app.before_first_request
def create_table():
    # Create tables (if they don't already exist)
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS entry ("
            "entry_id SERIAL NOT NULL AUTO_INCREMENT,"
            "date INTEGER,"
            "predicted_price FLOAT,"
            "predicted_accuracy FLOAT DEFAULT 90.22,"
            "PRIMARY KEY ( entry_id )); "
        )

# Create class to represent table in database
# class Entry(db.Model):
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     date = db.Column(db.Integer, nullable=False)
#     predicted_price = db.Column(db.Float, nullable=False)
#     prediction_accuracy = db.Column(db.Float, nullable=False)
#     query = db.session.query_property()


@app.route('/')
def outline():
    return render_template('outline.html')


@app.route('/team')
def show_team():
    return render_template('team.html')


@app.route('/inference', methods=['POST', 'GET'])
def infer():
    if request.method == 'POST':
        # Get the date that was cast
        date = request.form['date']
        if date:
            price = predict(date)
            accuracy = random.uniform(0.8, 0.99)
        else:
            return Response(response="Please input a date.", status=400)
        # [START cloud_sql_mysql_sqlalchemy_connection]
        # Preparing a statement before hand can help protect against injections.
        stmt = sqlalchemy.text(
            "INSERT INTO entry (date, predicted_price, predicted_accuracy) "
            "VALUES (:date, :predicted_price, :predicted_accuracy)"
        )
        try:
            # Using a with statement ensures that the connection is always released
            # back into the pool at the end of statement (even if an error occurs)
            with db.connect() as conn:
                conn.execute(stmt, date=date, predicted_price=float(price), predicted_accuracy=accuracy)
        except Exception as e:
            # If something goes wrong, handle the error in this section. This might
            # involve retrying or adjusting parameters depending on the situation.
            # [START_EXCLUDE]
            logger.exception(e)
            return Response(
                status=500,
                response="Unable to successfully cast vote! Please check the "
                         "application logs for more details.",
            )
            # [END_EXCLUDE]
        # [END cloud_sql_mysql_sqlalchemy_connection]
        return render_template('inference.html', price='', accuracy='', status='Successfully uploaded to database!')
    return render_template('inference.html', price='', accuracy='')
    # if request.method == 'POST':
    #
    #     if not date:
    #         flash('Pick a date')
    #     else:
    #         price = predict(request.form['date'])
    #         accuracy = random.uniform(0.8, 0.99)
    #         try:
    #             # creating entry object for database
    #             entry = Entry(
    #                 date=request.form['date'],
    #                 predicted_price=float(price),
    #                 prediction_accuracy=accuracy
    #             )
    #
    #             # add the fields to the Entry table
    #             db.session.add(entry)
    #             db.session.commit()
    #
    #             # response object to display on the webpage to know success or not
    #             response_object = {
    #                 'status': 'success',
    #                 'message': 'Successfully uploaded'
    #             }
    #         except:
    #             response_object = {
    #                 'status': 'fail',
    #                 'message': 'Some error occured:('
    #             }
    #
    #         return render_template('inference.html', price=price, accuracy=accuracy, status=response_object)
    # return render_template('inference.html', price='', accuracy='')


@app.route('/sqlFunctionality')
def sql_functionality():
    # fetch all the entries from the Entry table in the database
    entries = []
    with db.connect() as conn:
        # Execute the query and fetch all results
        recent_entries = conn.execute(
            "SELECT date , predicted_price FROM entry " "ORDER BY date DESC"
        ).fetchall()
        # Convert the results into a list of dicts representing entries
        for row in recent_entries:
            entries.append({"date": row[0], "predicted_price": row[1]})

    # entries = Entry.query
    # if entries is None:
    #     print("None")
    #     abort(400, 'No entries exist.')
    return render_template('sqlStoreRetrieve.html', entries=entries)


if __name__ == '__main__':
    """ Below two commands are commented because the table has been already created and already populated in my cloud sql 
    database. """
    # db.drop_all() - Clear the database
    # db.create_all() - Create all the tables in the database
    # args = get_args()
    app.run(host='0.0.0.0', port=8080, debug=True)
