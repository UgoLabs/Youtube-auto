from huggingface_hub import login, HfApi
from dotenv import load_dotenv
import os

def setup_huggingface():
    load_dotenv()
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_TOKEN not found in .env file")
    
    # Login to Hugging Face
    login(token=token, write_permission=True)
    
    # Verify login
    api = HfApi()
    user = api.whoami()
    print(f"Successfully logged in as: {user['name']}")

if __name__ == "__main__":
    setup_huggingface()