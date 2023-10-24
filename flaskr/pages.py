from flask import render_template, request, redirect, url_for, session, make_response
from flaskr.backend import Backend
import json


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
        game_in_progress = 'False'
        resp = make_response(
            render_template("play.html",
                                value = value,
                                username = username,
                                welcome = welcome,
                                game_in_progress = game_in_progress))
        resp.set_cookie('welcome', '', expires = 0)
        return resp

    @app.route('/collection')
    def collection():
        value = request.cookies.get('value')
        username = request.cookies.get('username')
        welcome = True
        message = ''

        # When a user clicks 'give up', they are redirected here. When they are, we need to restart session variables
        session['selected_player'] = ''
        session['guesses'] = 0
        
        backend = Backend('nba-user-credentials', bucket_client)

        # Access the user collection
        collection = backend.get_player_collection(username)

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
    
    @app.route("/nba22_23", methods = ['GET', 'POST']) 
    def nba22_23():
        value = request.cookies.get('value')
        username = request.cookies.get('username')
        welcome = True

        # Initializing variables
        game_in_progress = ''
        message = ''
        player_image = ''
        hints_used = set()
        selected_player = -1
        new_hint = ''
        hints_to_display = ''
        guesses = 0

        # Set this to false automatically, will be set to True if a new hint is requested
        get_new_hint = False
        new_guess = False

        # Create backend instance, accessing 'nba-user-credentials' bucket, this will allow us to access certain info (like collection) as well as use methods in the backend
        backend = Backend('nba-user-credentials', bucket_client)
        collection = backend.get_player_collection(username)

        # Get cards_data which holds all player information 
        csv_file = 'flaskr/player_information.csv'
        cards_data = backend.read_csv_file(csv_file)

        '''
        If the web app is using the 'GET' method, then the game should be on the start screen. 
        We will set up all game variables and then the user is prompted to begin the game if they desire to play.
        '''
        if request.method == 'GET':
            # Game hasn't started yet, it will when the user clicks the start button
            game_in_progress = 'False'

            # Select a valid player from cards_data using the user's collection, this is done through a backend method
            selected_player = backend.select_random_player(cards_data, collection)

            # In the case selected_player == None, then that means all players are already a part of the user's collection. 
            # We may avoid all the extra variables and just exit this if statement
            if not selected_player:
                message = "You've guessed all players, congratulations!"

            # In the case that the selected player is valid, then we can form the rest of the variables in the else branch
            else:
                # Get the link for the player's image
                player_image_links = backend.generate_links(cards_data)
                player_image = player_image_links[selected_player]
            
                # Get the first hint to display as well as its associated index number
                new_hint, new_hint_number = backend.get_hint(cards_data, collection, selected_player, hints_used)
                hints_used.add(new_hint_number)

                # Initialize game variables within the session, such as selected player to display, guess #, 
                session['guesses'] = guesses
                session['selected_player'] = selected_player
                session['player_image'] = player_image
                session['hints_to_display'] = ['???', '???', '???', '???', '???']
                session['hints_to_display'][new_hint_number] = new_hint
            # Bottom of method = 'get' 
        
        '''
        If the web app is using the 'POST' method, then we should be in game by this point. 
        We will check certain variables to indicate if the user is attempting a guess or requesting a new hint.
        '''  
        if request.method == 'POST':
            # Access variables within the session and reinitialize them so we can pass them back through the response
            player_image = session['player_image']
            selected_player = session['selected_player']

            # Access hints_to_display to determine which hints have been revealed
            hints_to_display = session['hints_to_display']
            for i in range(len(hints_to_display)):
                if hints_to_display[i] != '???':
                    # This is reinitializing the hints_used set, needed when retreiving a new hint from the backend
                    hints_used.add(i)

            # These 'new' variables will be true if the player just submitted a new guess or a request for a new hint
            get_new_hint = request.form.get('get_new_hint')
            new_guess = request.form.get('new_guess')

            # If get_new_hint is true, then we must retrieve the new hint and return it within 'hints_to_display'
            if get_new_hint == 'True':
                get_new_hint = True
                guesses = session['guesses']

                # Retrieve new hint, add it into the hints_used 
                new_hint, new_hint_number = backend.get_hint(cards_data, collection, selected_player, hints_used)

                if new_hint:
                    hints_used.add(new_hint_number)
                    hints_to_display[new_hint_number] = new_hint

                    # Save changes within the session
                    session['hints_to_display'] = hints_to_display

                # get_new_hint may be true, but that does not mean that there are any hints left. If new_hint is None, state that there are no hints left
                else:
                    message = "You don't have any hints left!"
                # Bottom of if statement for new hints

            # get_new_hint is False, so in the else-if case check if there was a guess attempt
            elif new_guess == 'True':
                # Increment the # of guesses
                session['guesses'] += 1
                guesses = session['guesses']

                # Retrieve guess attempt from the form
                guess_attempt = request.form['guess_attempt']

                # Check if the guess was correct, temporarily convert the spelling to ignore letter case for the comparison
                guess_lowercase = guess_attempt.lower()
                player_name_lowercase = cards_data[session['selected_player']][0].lower()
                if guess_lowercase == player_name_lowercase:

                    # The user correctly guessed the player! 
                    # Now the user's guess # and # of hints_used will be recorded in the users collection and uploaded to the bucket
                    # Do that within the following method in the backend
                    record_user_victory = backend.record_user_victory(collection, hints_used, session['selected_player'], session['guesses'], username)
                    if record_user_victory:
                        game_in_progress = 'False'
                        new_card_message = "You guessed correctly! Here's a new card for your collection :D"
                        new_card = 'True'
                        selected_player = session['selected_player']
                        collection = backend.get_player_collection(username)
                        player_image_links = backend.generate_links(cards_data)

                        # Clear the session
                        session.clear()

                        resp = make_response(
                                render_template("collection.html",
                                                value = value,
                                                username = username,
                                                welcome = welcome,
                                                new_card_message = new_card_message,
                                                new_card = new_card,
                                                selected_player = selected_player,
                                                cards_data = cards_data,
                                                collection = collection,
                                                player_image_links = player_image_links))
                        return resp
                    else:
                        print("For whatever reason, the W wasn't recorded properly")
                else:
                    message = 'That guess was incorrect, try again you got it!'
            # Bottom of method = 'post'

        resp = make_response(
                render_template("nba22_23.html",
                                value = value,
                                username = username,
                                welcome = welcome,
                                message = message,
                                game_in_progress = game_in_progress,
                                cards_data = cards_data,
                                player_image = player_image,
                                guesses = guesses,
                                hints_to_display = hints_to_display))
        return resp