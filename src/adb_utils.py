import subprocess
import re

def run_adb_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    return result.stdout.strip()

def check_for_device():
    output = run_adb_command(".\\platform-tools\\adb devices")
    lines = output.splitlines()
    for line in lines:
        if "\tdevice" in line:
            return line.split("\t")[0]
    return None

def get_installed_version(device_id):
    command = f".\\platform-tools\\adb -s {device_id} shell dumpsys package com.example.drumbeat | findstr versionName"
    output = run_adb_command(command)
    version_match = re.search(r'versionName=(\S+)', output)
    return version_match.group(1) if version_match else "Unknown"
