import sys
import os
import subprocess
import requests
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtCore import QThread, pyqtSignal
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

GITHUB_REPO = os.getenv('GITHUB_REPO')
LOCAL_APK_PATH = os.getenv('LOCAL_APK_PATH')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

class DownloadDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Downloading APK")
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()
        self.label = QLabel("Downloading APK, please wait...")
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress bar
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def close_event(self):
        self.accept()

class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, apk_url, headers, save_path):
        super().__init__()
        self.apk_url = apk_url
        self.headers = headers
        self.save_path = save_path

    def run(self):
        try:
            response = requests.get(self.apk_url, headers=self.headers, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(self.save_path, 'wb') as apk_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        apk_file.write(chunk)
                        downloaded_size += len(chunk)
                        progress = int(100 * downloaded_size / total_size)
                        self.progress.emit(progress)

            self.finished.emit()
        except requests.exceptions.RequestException as e:
            self.error.emit(str(e))

class InstallWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            # Run the PowerShell installation command
            result = subprocess.run(self.command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # Emit progress to show completion (since we can't track real-time progress, we simulate it)
            self.progress.emit(100)
            self.finished.emit()
        except subprocess.CalledProcessError as e:
            self.error.emit(f"Installation failed: {e.stderr}")


# Function to run ADB command and return output
def run_adb_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    return result.stdout.strip()

# Function to check if a device is connected
def check_for_device():
    output = run_adb_command(".\\platform-tools\\adb devices")
    lines = output.splitlines()
    for line in lines:
        if "\tdevice" in line:
            return line.split("\t")[0]
    return None

# Function to get installed version of Operativo
def get_installed_version(device_id):
    command = f".\\platform-tools\\adb -s {device_id} shell dumpsys package com.example.drumbeat | findstr versionName" # Note: to be changed to com.example.operativo 
    output = run_adb_command(command)
    version_match = re.search(r'versionName=(\S+)', output)
    return version_match.group(1) if version_match else "Unknown"

# Function to compare versions
def is_newer_version(latest_version, installed_version):
    from packaging import version
    latest_version_clean = latest_version.lstrip('v')
    installed_version_clean = installed_version.lstrip('v')
    print(f"The installed version is {installed_version}")
    
    try:
        return version.parse(latest_version_clean) > version.parse(installed_version_clean)
    except Exception as e:
        print(f"Version comparison error: {e}")
        return False

# Function to get the latest release from GitHub
def get_latest_release():
    try:
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        
        latest_release_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(latest_release_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        
        latest_release = response.json()
        print("GitHub API Response:", latest_release)
        
        return latest_release
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        QMessageBox.critical(None, "API Error", f"An error occurred while fetching the latest release: {e}")
        return None
    except Exception as e:
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        print(f"Unexpected Error: {error_message}")
        QMessageBox.critical(None, "Unexpected Error", f"An unexpected error occurred: {e}")
        return None

def download_apk(latest_release):
    try:
        # Look for the APK asset in the release's assets
        apk_asset = None
        for asset in latest_release.get('assets', []):
            if asset['name'].endswith('.apk'):
                apk_asset = asset
                break
        
        if apk_asset:
            apk_url = apk_asset['url']
            print(f"APK Download URL: {apk_url}")
            
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/octet-stream"
            }

            # Create and show the download dialog
            dialog = QDialog(window)
            dialog.setWindowTitle("Downloading APK")
            dialog.setFixedSize(300, 100)

            layout = QVBoxLayout()
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            layout.addWidget(QLabel("Downloading APK, please wait..."))
            layout.addWidget(progress_bar)
            dialog.setLayout(layout)
            dialog.show()

            # Create the worker thread
            worker = DownloadWorker(apk_url, headers, LOCAL_APK_PATH)
            worker.progress.connect(progress_bar.setValue)
            worker.finished.connect(dialog.accept)
            worker.error.connect(lambda msg: QMessageBox.critical(window, "Download Failed", msg))
            worker.finished.connect(lambda: QMessageBox.information(window, "Download Complete", "The latest APK has been downloaded."))
            worker.start()

            dialog.exec_()

        else:
            QMessageBox.warning(window, "Download Failed", "Could not find the APK in the latest release.")
    except Exception as e:
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        print(f"Unexpected Error: {error_message}")
        QMessageBox.critical(window, "Unexpected Error", f"An unexpected error occurred: {e}")


# Function to check for update and initiate APK download
def check_for_update():
    latest_release = get_latest_release()
    
    if latest_release:
        latest_version = latest_release.get('tag_name')
        if latest_version is None:
            QMessageBox.warning(window, "No Version Found", "The latest release does not have a tag name.")
            return
        
        installed_version = installed_version_label.text()
        
        if is_newer_version(latest_version, installed_version):
            download_apk(latest_release)
        else:
            QMessageBox.information(window, "No Update Available", "You are already on the latest version.")

# Function to install the APK using the bat script
def install_apk():
    try:
        command = "powershell.exe -ExecutionPolicy Bypass -File install_app.ps1"

        # Create and show the installation dialog
        dialog = QDialog(window)
        dialog.setWindowTitle("Installing APK")
        dialog.setFixedSize(300, 100)

        layout = QVBoxLayout()
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        layout.addWidget(QLabel("Installing APK, please wait..."))
        layout.addWidget(progress_bar)
        dialog.setLayout(layout)
        dialog.show()

        # Create the worker thread for installation
        worker = InstallWorker(command)
        worker.progress.connect(progress_bar.setValue)
        worker.finished.connect(dialog.accept)
        worker.error.connect(lambda msg: QMessageBox.critical(window, "Installation Failed", msg))
        worker.finished.connect(lambda: QMessageBox.information(window, "Installation Complete", "The app has been installed successfully."))
        worker.start()

        dialog.exec_()

    except Exception as e:
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        print(f"Unexpected Error: {error_message}")
        QMessageBox.critical(window, "Unexpected Error", f"An unexpected error occurred: {e}")

# PyQt Application
app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Operativo Installer")

layout = QVBoxLayout()

status_label = QLabel("Waiting for connection to tablet.")
status_label.setAlignment(Qt.AlignCenter)
layout.addWidget(status_label)

device_id_label = QLabel("Device ID: N/A")
device_id_label.setAlignment(Qt.AlignCenter)
layout.addWidget(device_id_label)

installed_version_label = QLabel("Installed Version: N/A")
installed_version_label.setAlignment(Qt.AlignCenter)
layout.addWidget(installed_version_label)

check_update_button = QPushButton("Check for Update")
check_update_button.setEnabled(False)
check_update_button.clicked.connect(check_for_update)
layout.addWidget(check_update_button)

install_button = QPushButton("Install Operativo")
install_button.setEnabled(False)
install_button.clicked.connect(install_apk)
layout.addWidget(install_button)

window.setLayout(layout)

# Timer to periodically check for device connection
def update_status():
    device_id = check_for_device()
    if device_id:
        status_label.setText("Tablet Connected")
        device_id_label.setText(f"Device ID: {device_id}")
        installed_version = get_installed_version(device_id)
        installed_version_label.setText(installed_version)
        check_update_button.setEnabled(True)
        install_button.setEnabled(True)
    else:
        status_label.setText("Waiting for connection to tablet.")
        device_id_label.setText("Device ID: N/A")
        installed_version_label.setText("Installed Version: N/A")
        check_update_button.setEnabled(False)
        install_button.setEnabled(False)

timer = QTimer()
timer.timeout.connect(update_status)
timer.start(2000)  # Check every 2 seconds

window.show()
sys.exit(app.exec_())
