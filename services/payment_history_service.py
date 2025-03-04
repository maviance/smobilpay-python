import requests
from models.payment_history_model import PaymentHistoryModel
from s3_api_auth import S3ApiAuth
from configuration import Configuration  # Import the configuration class
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PaymentHistoryService:
    def __init__(self, public_token=None, secret_key=None):
        self.config = Configuration()  # Create a configuration instance
        self.public_token = public_token if public_token else self.config.get_api_key()
        self.secret_key = secret_key if secret_key else self.config.get_api_secret()
        self.api_version = self.config.api_version
        self.base_url = f"{self.config.get_api_url()}/historystd"
        self.api_auth = S3ApiAuth(self.base_url, self.public_token, self.secret_key)

    def fetch_payment_history(self, timestamp_from=None, timestamp_to=None):
        params = {}
        if timestamp_from:
            try:
                params['timestamp_from'] = timestamp_from
            except AttributeError:
                logging.error("Invalid type for timestamp_from. It must be a datetime object.")
                return "Invalid timestamp_from provided."
        if timestamp_to:
            try:
                params['timestamp_to'] = timestamp_to
            except AttributeError:
                logging.error("Invalid type for timestamp_to. It must be a datetime object.")
                return "Invalid timestamp_to provided."
        headers = {
            'Authorization': self.api_auth.create_authorization_header('GET', params),
            'x-api-version': self.api_version
        }

        return self._make_request(params, headers)

    def _make_request(self, params, headers):
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            if response.status_code == 200:
                history_data = response.json()
                return [PaymentHistoryModel(**item) for item in history_data]
            elif response.status_code == 401:
                logging.error("Request could not be authenticated: %s", response.text)
                return "Request could not be authenticated."
            else:
                logging.error("An error occurred with status code: %s and payload %s", response.status_code, response.content)
                return "An unexpected error occurred."
            
        except requests.RequestException as e:
            logging.error("Network error occurred: %s", str(e))
            return f"Network error occurred: {str(e)}"
