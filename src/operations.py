from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QMessageBox
from install_worker import InstallWorker

def install_apk(window):
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
