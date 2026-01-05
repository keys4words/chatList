Write-Host "Building executable..." -ForegroundColor Green
pyinstaller --onefile --windowed --name "ChatList" main.py
Write-Host ""
Write-Host "Build complete! Check the 'dist' folder for the executable." -ForegroundColor Green
Read-Host "Press Enter to continue"

