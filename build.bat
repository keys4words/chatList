@echo off
echo Building executable...
python -c "from version import __version__; print(__version__)" > temp_version.txt
set /p VERSION=<temp_version.txt
del temp_version.txt
pyinstaller --onefile --windowed --name "ChatList-v%VERSION%" --icon=app.ico main.py
echo.
echo Build complete! Check the 'dist' folder for ChatList-v%VERSION%.exe
pause
