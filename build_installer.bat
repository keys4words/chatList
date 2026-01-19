@echo off
echo Building executable...
call build.bat

echo.
echo Generating setup.iss...
python generate_setup.py

echo.
echo Building installer with Inno Setup...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    "C:\Program Files\Inno Setup 6\ISCC.exe" setup.iss
) else (
    echo Inno Setup не найден! Установите Inno Setup 6 и добавьте его в PATH.
    echo Или запустите ISCC.exe вручную с файлом setup.iss
    pause
    exit /b 1
)

echo.
echo Installer build complete! Check the 'installer' folder.
pause

