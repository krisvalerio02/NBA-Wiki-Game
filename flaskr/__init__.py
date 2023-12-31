from flaskr import pages
from flask import Flask
from google.cloud import storage
#from .backend_test import BucketClientMock

import logging
logging.basicConfig(level=logging.DEBUG)

# The flask terminal command inside "run-flask.sh" searches for
# this method inside of __init__.py (containing flaskr module 
# properties) as we set "FLASK_APP=flaskr" before running "flask".
def create_app(test_config=None):

    # Create and configure the app.
    app = Flask(__name__, instance_relative_config=True)

    # This is the default secret key used for login sessions
    # By default the dev environment uses the key 'dev'
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing.
        # This file is not committed. Place it in production deployments.
        app.config.from_pyfile('config.py', silent=True)

        # Create bucket_client which is an instance of the storage client from Google Cloud
        bucket_client = storage.Client()

    else:
        # Load the test config if passed in.
        app.config.from_mapping(test_config)
        #bucket_client = BucketClientMock()

    # Make additional modifications here for logging in, backend and additional endpoints.
    pages.make_endpoints(app, bucket_client)
    return app
