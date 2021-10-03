import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode. Set to False if converting to GUI
DEBUG = False

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
SECRET_KEY = 'cfec8f22304e40012b2ad7abf63eb01a100cfea3d977d588'

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False