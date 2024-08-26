import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer, Qt
from config import load_environment_variables
from adb_utils import check_for_device, get_installed_version
from github_utils import check_for_update
from operations import install_apk

# Load environment variables
global GITHUB_REPO, LOCAL_APK_PATH, GITHUB_TOKEN
GITHUB_REPO, LOCAL_APK_PATH, GITHUB_TOKEN = load_environment_variables()

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
check_update_button.clicked.connect(lambda: check_for_update(installed_version_label.text()))
layout.addWidget(check_update_button)

install_button = QPushButton("Install Operativo")
install_button.setEnabled(False)
install_button.clicked.connect(lambda: install_apk(window))
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
