import argparse
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = os.urandom(256)

def get_args():
    args = getattr(get_args, '_args', None)
    if args is None:
        parser = argparse.ArgumentParser()

        # Only used when running the flask debugging server
        parser.add_argument(
            '-H', '--host', default='0.0.0.0',
            help='Address for the debug webserver to listen on.')
        parser.add_argument(
            '-P', '--port', default='8080', type=int,
            help='Port for webserver to listen on.')

        parser.add_argument(
            '-d', '--db-host',
            default=os.environ.get('DB_HOST', '127.0.0.1'),
            help='Host address of the database.')
        parser.add_argument(
            '-n', '--db-name',
            default=os.environ.get('DB_NAME', 'cc_final_database'),
            help='Name of the database.')
        parser.add_argument(
            '-c', '--db-cona',
            default=os.environ.get('DB_CONNECTION_NAME', 'cc-final-296102:us-east4:cc-final-database'),
            help='Connection name of the instance.')
        parser.add_argument(
            '-u', '--db-user',
            default=os.environ.get('DB_USER', 'root'),
            help='User used to connect to the database.')
        parser.add_argument(
            '-p', '--db-pass',
            default=os.environ.get('DB_PASS', 'team11DataBases'),
            help='Password used to connect to the database.')


        args = get_args._args = parser.parse_args()
    return args


def get_db_uri():
    args = get_args()
    # a = 'mysql+pymysql://{}:{}@{}/{}?unix_socket=/cloudsql/{}'.format(
    #     args.db_user, args.db_pass, args.db_host, args.db_name, args.db_cona)
    # print(a)
    # return a
    return 'mysql+pymysql://{}:{}@{}/{}'.format(
        args.db_user, args.db_pass, args.db_host, args.db_name)


# SQLALCHEMY_TRACK_MODIFICATIONS = False
#
# # GCP
# CLOUDSQL_USER = 'root'
# CLOUDSQL_PASSWORD = 'team11DataBases'
# CLOUDSQL_DATABASE = 'cc_final_database'
# CLOUDSQL_CONNECTION_NAME = 'cc-final-296102:us-east4:cc-final-database'
# LOCAL_SQLALCHEMY_DATABASE_URI = (
#     'mysql+pymysql://{nam}:{pas}@127.0.0.1:3306/{dbn}').format(
#     nam=CLOUDSQL_USER,
#     pas=CLOUDSQL_PASSWORD,
#     dbn=CLOUDSQL_DATABASE,
# )
#
# LIVE_SQLALCHEMY_DATABASE_URI = (
#     'mysql+pymysql://{nam}:{pas}@127.0.0.1:3306/{dbn}?unix_socket=/cloudsql/{con}').format(
#     nam=CLOUDSQL_USER,
#     pas=CLOUDSQL_PASSWORD,
#     dbn=CLOUDSQL_DATABASE,
#     con=CLOUDSQL_CONNECTION_NAME,
# )
#
# SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI

# if True:
#
# else:
#     SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI

# Override to SQLITE (for testing ...)
# SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
