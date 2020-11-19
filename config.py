import os

SECRET_KEY = os.urandom(256)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# GCP
CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'team11DataBases'
CLOUDSQL_DATABASE = 'cc_final_database'
CLOUDSQL_CONNECTION_NAME = 'cc-final-296102:us-east4:cc-final-database'
LOCAL_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{nam}:{pas}@127.0.0.1:3306/{dbn}').format(
    nam=CLOUDSQL_USER,
    pas=CLOUDSQL_PASSWORD,
    dbn=CLOUDSQL_DATABASE,
)

LIVE_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{nam}:{pas}@localhost/{dbn}?unix_socket=/cloudsql/{con}').format(
    nam=CLOUDSQL_USER,
    pas=CLOUDSQL_PASSWORD,
    dbn=CLOUDSQL_DATABASE,
    con=CLOUDSQL_CONNECTION_NAME,
)

SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI

# if True:
#
# else:
#     SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI

# Override to SQLITE (for testing ...)
# SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
