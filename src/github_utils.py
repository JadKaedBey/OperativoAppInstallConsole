import requests
from PyQt5.QtWidgets import QMessageBox
from config import load_environment_variables
from ui_components import download_apk

GITHUB_REPO, _, GITHUB_TOKEN = load_environment_variables()

def get_latest_release():
    try:
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        
        latest_release_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(latest_release_url, headers=headers)
        response.raise_for_status()
        
        latest_release = response.json()
        print("GitHub API Response:", latest_release)
        
        return latest_release
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        QMessageBox.critical(None, "API Error", f"An error occurred while fetching the latest release: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        QMessageBox.critical(None, "Unexpected Error", f"An unexpected error occurred: {e}")
        return None
    
def check_for_update(installed_version):
    latest_release = get_latest_release()
    
    if latest_release:
        latest_version = latest_release.get('tag_name')
        if latest_version is None:
            QMessageBox.warning(None, "No Version Found", "The latest release does not have a tag name.")
            return
        
        if is_newer_version(latest_version, installed_version):
            download_apk(latest_release)
        else:
            QMessageBox.information(None, "No Update Available", "You are already on the latest version.")

def is_newer_version(latest_version, installed_version):
    from packaging import version
    latest_version_clean = latest_version.lstrip('v')
    installed_version_clean = installed_version.lstrip('v')
    
    try:
        return version.parse(latest_version_clean) > version.parse(installed_version_clean)
    except Exception as e:
        print(f"Version comparison error: {e}")
        return False
