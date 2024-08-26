# install_app.ps1

$adb_path = ".\platform-tools\adb.exe"
$apk_path = ".\operativo_latest.apk"  # Make sure this path is correct

# Install the APK on the connected device
& $adb_path install -r $apk_path

# Check the exit code
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install APK."
    exit $LASTEXITCODE
}
