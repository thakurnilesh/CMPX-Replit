import requests

class APIClient:
    def __init__(self, endpoint, username, password):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        
    def post_data(self, payload):
        """
        Post the JSON payload to the API endpoint using Basic Auth.
        """
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                auth=(self.username, self.password)
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")