@echo off
echo Checking for Inno Setup installation...

REM Check common installation paths
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    goto :build
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
    goto :build
)
if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    goto :build
)
if exist "C:\Program Files\Inno Setup 5\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 5\ISCC.exe"
    goto :build
)

echo Inno Setup not found!
echo.
echo Please download and install Inno Setup from:
echo https://jrsoftware.org/isdl.php
echo.
echo After installation, run this script again to build the installer.
pause
exit /b 1

:build
echo Found Inno Setup at: %ISCC_PATH%
echo.
echo Building installer...
"%ISCC_PATH%" setup.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Installer built successfully! Check the 'installer' folder.
) else (
    echo.
    echo Error building installer. Exit code: %ERRORLEVEL%
    pause
    exit /b 1
)

pause

