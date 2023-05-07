from flask import render_template
import requests
from flaskr.backend import Backend


def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when 
    # users go to a specific route on the project's website.

    @app.route("/")
    def home():
        
        return render_template("home.html")
    
    @app.route("/about")
    def about():

        return render_template("about.html")
    
    @app.route("/login")
    def login():

        return render_template('login.html')

    @app.route("/signup")
    def signup():

        return render_template('signup.html')