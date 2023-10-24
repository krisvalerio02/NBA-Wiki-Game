import hashlib
import json
import csv
import random

'''
Backend contains methods used for various under-the-cover functions,
such as storing, accessing, modifying, and organizing data.
'''

class Backend:

    '''
    Initialize an instance of the GCS buckets
    '''
    def __init__(self, bucket_name, bucket_client):
        self.bucket_name = bucket_name
        # bucket_client is an instance of a storage client which is from the Google Cloud
        self.bucket = bucket_client.bucket(bucket_name)

    '''
    Adds user name and password to bucket if it does not exist in the bucket
    '''
    def sign_up(self, username, password):
        prefixed_password = 'nba_wiki_game' + password
        hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()
        password_blob = self.bucket.blob(f"{username}_password")
        if password_blob.exists():
            return False
        else:
            password_blob.upload_from_string(hashed_password)
            
            # Initialize empty dictionary which will holds user's collection (player ID as key and value is medal string)
            collection = dict()

            # Convert dictionary to JSON string
            json_data = json.dumps(collection)

            # Upload collection blob
            collection_blob = self.bucket.blob(f"{username}_collection")
            collection_blob.upload_from_string(json_data)
            return True

    def log_in(self, username, password):
        '''
        Checks if the password (hashed) matches the password associated to the 
        username in the bucket
        '''
        prefixed_password = 'nba_wiki_game' + password
        hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()
        password_blob = self.bucket.blob(f"{username}_password")
        if password_blob.exists():

            # Access stored password (associated to username) and compare inputted password
            bucket_password = password_blob.download_as_bytes().decode('utf-8')
            if hashed_password == bucket_password:
                return True
        return False

    def get_player_collection(self, username):
        '''
        Method will access the user's collection which should consist of a dictionary -
        {keys are player ID's they've collected : value is a tuple [medal, tries]}
        '''
        collection_blob = self.bucket.blob(f"{username}_collection")

        # Get the collection (json data) from the collection blob, then convert that json_data into a functional dict
        json_data = collection_blob.download_as_string().decode('utf-8')
        json_dict = json.loads(json_data)

        # Load up collection (functional dict) manually by traversing the json_dict
        collection = dict()
        for key in json_dict:
            collection[int(key)] = json_dict[key]
        return collection
    
    def read_csv_file(self, file_path):
        '''
        Method reads and parses csv file
        '''
        data = []
        with open(file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                data.append(row)
        return data
    
    def generate_links(self, cards_data):
        '''
        Method generates links for all NBA player images using the players names
        '''
        links = list()
        for player_id in range(len(cards_data)):

            # Converts player name into all lowercase, then splits the string by spaces into a list (Stephen Curry -> ['stephen', 'curry'])
            temp = cards_data[player_id][0].lower().split()
            links.append('https://storage.cloud.google.com/nba-players/' + temp[0] + '_' + temp[1] + '_image.png?authuser=1')

            # https://storage.cloud.google.com/nba-players/demar_derozan_image.png?authuser=1
        return links

    def get_hint(self, cards_data, collection, selected_player, hints_used):
        '''
        Method will determine a new random hint to display to the user using cards_data and the player's collection
        '''
        while len(hints_used) < 5:
            new_hint_number = random.randint(0, 4)

            # If the random hint corresponding to the random_int is NOT in hints_used, we can use this hint
            if new_hint_number not in hints_used:

                # If hint #0, extract first letter of player name only
                if new_hint_number == 0:
                    return cards_data[selected_player][0][0], new_hint_number
            
                return cards_data[selected_player][new_hint_number], new_hint_number
            
        return None, None

    def select_random_player(self, cards_data, collection):
        '''
        Method will select a random valid player to use for the guessing game
        '''
        while len(collection) < len(cards_data):
            random_int = random.randint(0, len(cards_data) - 1)

            # Check if the player is in the user's collection
            if random_int not in collection.keys():
                return random_int
        
        # If len of user collection is >= len of cards_data, there are no players left
        return None

    def record_user_victory(self, collection, hints_used, selected_player, guesses, username):
        '''
        Method receives user metadata in terms of how they did in the game, record that in their collection and upload to bucket
        '''
        medal = ''
        if len(hints_used) > 2:
            medal = 'Bronze'
        elif len(hints_used) > 1:
            medal = 'Silver'
        else:
            medal = 'Gold'
        
        # Add the updates to the collection and then convert it into json format
        collection[selected_player] = [medal, guesses]
        json_collection = json.dumps(collection)

        # Initalize the collection blob in which we are going to upload the updated dictionary to
        collection_blob = self.bucket.blob(f"{username}_collection")

        # Upload collection blob
        collection_blob.upload_from_string(json_collection)
        return True