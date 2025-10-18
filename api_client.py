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
    
    def patch_data(self, identifier, payload):
        """
        Update (PATCH) an existing migration package with Configuration items.
        
        Args:
            identifier: The package identifier (e.g., "packagename_v1")
            payload: The JSON payload containing Configuration items
        """
        try:
            # Construct the update endpoint
            update_endpoint = self.endpoint.replace('/rest/v14/', '/rest/v19/')
            update_endpoint = f"{update_endpoint}/{identifier}"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.patch(
                update_endpoint,
                json=payload,
                headers=headers,
                auth=(self.username, self.password)
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"API PATCH request failed: {str(e)}")