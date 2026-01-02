@echo off
echo Building executable...
pyinstaller --onefile --windowed --name "MinimalPyQtApp" app.py
echo.
echo Build complete! Check the 'dist' folder for the executable.
pause

