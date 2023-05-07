#!/usr/bin/env bash

# Shortcut ./run-flask.sh

export FLASK_APP=flaskr
export FLASK_ENV=development
export GOOGLE_CLOUD_PROJECT=NBA-Wiki-Game
flask run -p 8080