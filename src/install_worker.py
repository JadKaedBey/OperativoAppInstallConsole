from PyQt5.QtCore import QThread, pyqtSignal
import subprocess

class InstallWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            result = subprocess.run(self.command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.progress.emit(100)
            self.finished.emit()
        except subprocess.CalledProcessError as e:
            self.error.emit(f"Installation failed: {e.stderr}")
