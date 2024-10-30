from openai import OpenAI
from openai import AuthenticationError, APIConnectionError
import os

def test_openai_connection():
    #Test the OpenAI API connection using the configured API key.
    try:
        client = OpenAI()
        # Make a minimal API call to test authentication
        client.models.list()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return True, f"API connection successful! Using model: {model}"
    except AuthenticationError:
        return False, "Authentication failed. Please check your OpenAI API key."
    except APIConnectionError:
        return False, "Connection failed. Please check your internet connection."
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"
