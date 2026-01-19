Write-Host "Building executable..." -ForegroundColor Green

# Получаем версию из version.py
$version = python -c "from version import __version__; print(__version__)"
$version = $version.Trim()

Write-Host "Building version: $version" -ForegroundColor Cyan

pyinstaller --onefile --windowed --name "ChatList-v$version" --icon=app.ico main.py

Write-Host ""
Write-Host "Build complete! Check the 'dist' folder for ChatList-v$version.exe" -ForegroundColor Green
Read-Host "Press Enter to continue"
