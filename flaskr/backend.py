import hashlib

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
        blob = self.bucket.blob(username)
        if blob.exists():
            return False
        else:
            blob.upload_from_string(hashed_password)
            return True

    def log_in(self, username, password):
        '''
        Checks if the password (hashed) matches the password associated to the 
        username in the bucket
        '''
        prefixed_password = 'nba_wiki_game' + password
        hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()
        blob = self.bucket.blob(username)
        if blob.exists():
            # Access stored password (associated to username) and compare inputted password
            bucket_password = blob.download_as_bytes().decode('utf-8')
            if hashed_password == bucket_password:
                return True
        return False

    def get_image(self):
        pass

