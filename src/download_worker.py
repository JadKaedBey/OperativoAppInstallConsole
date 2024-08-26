from PyQt5.QtCore import QThread, pyqtSignal
import requests

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
