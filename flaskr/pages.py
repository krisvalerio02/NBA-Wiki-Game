from flask import render_template, request, redirect, url_for, session, make_response
from flaskr.backend import Backend


def make_endpoints(app, bucket_client):

    # Flask uses the "app.route" decorator to call methods when 
    # users go to a specific route on the project's website.

    @app.route("/")
    def home():
        # Get and set cookie information if a user is logged in, do this per route
        value = request.cookies.get('value')
        username = request.cookies.get('username')
        welcome = request.cookies.get('welcome')        
        return render_template("home.html",
                                value = value,
                                username = username,
                                welcome = welcome)
    
    @app.route("/about")
    def about():
        value = request.cookies.get('value')
        username = request.cookies.get('username')
        welcome = True
        resp = make_response(
            render_template("about.html",
                                value = value,
                                username = username,
                                welcome = welcome))
        resp.set_cookie('welcome', '', expires = 0)
        return resp
    
    @app.route("/login", methods = ['GET', 'POST'])
    def login():
        # Create backend instance, accessing 'nba-user-credentials' bucket
        backend = Backend('nba-user-credentials', bucket_client)
        message = ''

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # For cookies
            session['username'] = username

            # value is a boolean representing a successful or failed log in attempt
            value = backend.log_in(username, password) 
            if value:
                welcome = 'True'
                resp = make_response(
                    render_template('home.html', 
                                    value=value, 
                                    username=username,
                                    welcome=welcome))
                resp.set_cookie('value', 'True')
                resp.set_cookie('username', username)
                resp.set_cookie('welcome', 'True')
                return resp
            else:
                session['username'] = None
                message = 'ERROR: Your login attempt has failed. Make sure the username and password are correct.'
                return render_template('login.html', message = message)
        else:
            return render_template('login.html')

    @app.route('/signup', methods = ['GET', 'POST'])
    def signup():
        # Create backend instance, accessing 'nba-user-credentials' bucket
        backend = Backend('nba-user-credentials', bucket_client)

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # backend.sign_up() will sign the user up. If successful, True will be returned
            if backend.sign_up(username, password):
                return redirect(url_for('login'))
            else:
                message = "ERROR: username already exists."
                return render_template('signup.html', message=message)
        else:
            return render_template('signup.html')
    
    @app.route('/logout')
    def logout():
        resp = make_response(render_template('home.html'))
        # Reset cookie settings
        resp.set_cookie('value', '', expires = 0)
        resp.set_cookie('username', '', expires = 0)
        resp.set_cookie('welcome', '', expires = 0)
        session.pop('username', None)
        return resp

    @app.route('/play')
    def play():
        value = request.cookies.get('value')
        username = request.cookies.get('username')
        welcome = True
        resp = make_response(
            render_template("play.html",
                                value = value,
                                username = username,
                                welcome = welcome))
        resp.set_cookie('welcome', '', expires = 0)
        return resp

    @app.route('/collection')
    def collection():
        value = request.cookies.get('value')
        username = request.cookies.get('username')
        welcome = True
        message = ''

        backend = Backend('nba-user-credentials', bucket_client)

# Access the user collection
        collection = backend.get_player_collection(username)
        list_of_player_collection = []
        for player in collection:
            list_of_player_collection.append(int(player))
        print(list_of_player_collection)

# Access player_information.csv
        cards_data = backend.read_csv_file('flaskr/player_information.csv')

# Generate links for every player within a dictionary
        player_image_links = backend.generate_links(cards_data)

# Create message, if collection is empty then state that it is
        if len(collection) == 0:
            message = 'Your collection is currently empty, click on play to collect cards!'

        resp = make_response(
            render_template("collection.html",
                                value = value,
                                username = username,
                                welcome = welcome,
                                message = message,
                                cards_data = cards_data,
                                collection = collection,
                                player_image_links = player_image_links))
        resp.set_cookie('welcome', '', expires = 0)
        return resp
    
    @app.route("/nba22_23")
    def nba22_23():
        value = request.cookies.get('value')
        username = request.cookies.get('username')
        welcome = True

        # Access player_information.csv and parse the info. It will be used here

    
        # Create backend instance, accessing 'nba-user-credentials' bucket
        backend = Backend('nba-user-credentials', bucket_client)
        collection = backend.get_player_collection(username)

        backend.test_collection(username)
        
        backend.get_player_collection(username)

        print('HERES PAGES, COLLECTION:')
        print(collection)

        csv_file = 'flaskr/player_information.csv'
        cards_data = backend.read_csv_file(csv_file)
        print(cards_data[0][0])

        resp = make_response(
            render_template("nba22_23.html",
                                value = value,
                                username = username,
                                welcome = welcome))
        resp.set_cookie('welcome', '', expires = 0)
        return resp