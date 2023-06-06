import hashlib
import json
import csv

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
        
    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        pass

    def upload(self):
        pass

    def sign_up(self, username, password):
        '''
        Adds user name and password to bucket if it does not exist in the bucket
        '''
        prefixed_password = 'nba_wiki_game' + password
        hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()
        password_blob = self.bucket.blob(f"{username}_password")
        if password_blob.exists():
            return False
        else:
            password_blob.upload_from_string(hashed_password)
            
# Initialize dictionary which will holds user's collection (player ID as key and value is medal string)
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
        Method will access the user's collection which should consist of a dictionary,
        keys are player ID's they've collected and value is a tuple, index 0 = medal and index 1 = tries
        '''
        collection_blob = self.bucket.blob(f"{username}_collection")
# Get the collection (json data) from the collection blob, then convert that json_data into a functional dict
        json_data = collection_blob.download_as_string().decode('utf-8')
        json_dict = json.loads(json_data)
        collection = dict()
        for key in json_dict:
            collection[int(key)] = json_dict[key]
        return collection

    def test_collection(self, username):
        collection_blob = self.bucket.blob(f"{username}_collection")
        json_data = collection_blob.download_as_string().decode('utf-8')
        collection = json.loads(json_data)

# FOR NOW, WE WILL SET USER LEBRON INFO TO {0: [Gold, 3], which is steph and gold medal
        collection[0] = ['Gold', 3]
        collection[2] = ['Silver', 6]

# Convert collection back into json data
        updated_json_data = json.dumps(collection)
    
# Upload the updated JSON string as the content of the blob
        collection_blob.upload_from_string(updated_json_data)

        return

    
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
            links.append('https://storage.cloud.google.com/nba-players/' + temp[0] + '_' + temp[1] + '_image.png?authuser=3')
        
        return links

    def get_image(self):
        pass
