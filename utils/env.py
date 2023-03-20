from dotenv import load_dotenv
import os

load_dotenv()

def get_env(key):
    if val := os.getenv(key):
        return val
    else:
        raise ValueError(f"Environment variable {key} not set")