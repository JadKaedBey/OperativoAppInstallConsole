# Operativo Installer Console

## Overview

The Operativo Installer Console is a Python-based tool designed to facilitate the installation and updating of applications on Android devices. It provides a graphical user interface (GUI) for detecting connected devices, checking for updates from a GitHub repository, and installing the latest version of the application on the device.

## Features

- **Device Detection**: Automatically detects connected Android devices via USB.
- **Version Checking**: Retrieves the currently installed version of the application on the device.
- **Update Checking**: Compares the installed version with the latest release available on GitHub.
- **APK Download and Installation**: Downloads the latest APK from GitHub and installs it on the connected Android device.

## Prerequisites

- **Python 3.10 or higher**
- **ADB (Android Debug Bridge)**: ADB must be installed and configured in your system's PATH.
- **GitHub Token**: A personal access token (PAT) from GitHub is required to access the GitHub API.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/JadKaedBey/OperativoInstaller.git
   cd OperativoInstaller
   ```

2. **Activate a Virtual Environment**:

Simply use the run.bat executable, or:
   
   ```bash
     venv\Scripts\activate
   ```

3. **Configure Environment Variables**:
   - Create a `.env` file in the root directory of the project.
   - Add the following environment variables:
     ```env
     GITHUB_REPO=JadKaedBey/OperativoAppInstallConsole
     GITHUB_TOKEN= to be obtained by contacting me at jad.kaedbey@operativo.io
     LOCAL_APK_PATH=operativo_latest.apk
     ```

## Usage

1. **Start the Console**:
   - Run the main script to launch the GUI:

2. **Connect an Android Device**:
   - Connect your Android device to your computer via USB. Ensure that USB debugging is enabled on the device.

3. **Check for Updates**:
   - Click on the "Check for Update" button. The console will retrieve the latest release from the specified GitHub repository and compare it with the version installed on the device.

4. **Install the Application**:
   - If an update is available, the APK will be downloaded. Click on "Install Operativo" to install the APK on the connected device.
