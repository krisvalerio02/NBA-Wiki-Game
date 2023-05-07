from flask import render_template
import requests
from flaskr.backend import Backend


def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        
        return render_template("about.html")
    
    # @app.route("/about")
    # def about():
    #     return render_template("about.html")
    
    @app.route("/login")
    def login():
        print('rendering login template....')

        return render_template('login.html')

    # TODO(Project 1): Implement additional routes according to the project requirements.
