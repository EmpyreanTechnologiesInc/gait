from openai import OpenAI
from openai import AuthenticationError, APIConnectionError
from dotenv import load_dotenv
import os

def test_openai_connection():
    try:
        load_dotenv(override=True)  # Force reload environment variables
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False, "\033[1;31mAPI key not found in environment variables\033[0m. Set it in .env file."
        
        # Create a fresh client with the new key
        client = OpenAI(api_key=api_key)
        
        # Test the connection with a minimal API call
        models = client.models.list()  # Store the result to ensure the call completes
        
        model = os.getenv("OPENAI_MODEL")
        return True, f"API connection successful! Using model: {model}"
    except AuthenticationError as e:
        return False, f"\033[1;31mAuthentication failed\033[0m: {str(e)}"
    except APIConnectionError as e:
        return False, f"\033[1;31mConnection failed\033[0m: {str(e)}"
    except Exception as e:
        return False, f"\033[1;31mAn unexpected error occurred\033[0m: {str(e)}"

