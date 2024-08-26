import os
from dotenv import load_dotenv

def load_environment_variables():
    load_dotenv()
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    LOCAL_APK_PATH = os.getenv('LOCAL_APK_PATH')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    return GITHUB_REPO, LOCAL_APK_PATH, GITHUB_TOKEN
