from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QMessageBox
from download_worker import DownloadWorker
from config import load_environment_variables

GITHUB_REPO, LOCAL_APK_PATH, GITHUB_TOKEN = load_environment_variables()

def download_apk(latest_release):
    try:
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

            dialog = QDialog()
            dialog.setWindowTitle("Downloading APK")
            dialog.setFixedSize(300, 100)

            layout = QVBoxLayout()
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            layout.addWidget(QLabel("Downloading APK, please wait..."))
            layout.addWidget(progress_bar)
            dialog.setLayout(layout)
            dialog.show()

            worker = DownloadWorker(apk_url, headers, LOCAL_APK_PATH)
            worker.progress.connect(progress_bar.setValue)
            worker.finished.connect(dialog.accept)
            worker.error.connect(lambda msg: QMessageBox.critical(None, "Download Failed", msg))
            worker.finished.connect(lambda: QMessageBox.information(None, "Download Complete", "The latest APK has been downloaded."))
            worker.start()

            dialog.exec_()

        else:
            QMessageBox.warning(None, "Download Failed", "Could not find the APK in the latest release.")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        QMessageBox.critical(None, "Unexpected Error", f"An unexpected error occurred: {e}")
