# install_app.ps1

$adb_path = ".\platform-tools\adb.exe"
$apk_path = ".\operativo_latest.apk"  
$package_name = "com.example.drumbeat" 

# Uninstall the existing APK (ignore errors if not installed)
& $adb_path uninstall $package_name

# Install the APK on the connected device
& $adb_path install -r $apk_path

# Check the exit code
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install APK."
    exit $LASTEXITCODE
}
