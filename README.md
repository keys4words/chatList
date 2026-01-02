# chatList

A minimal Python application with PyQt GUI.

## Installation

Install the required dependencies:

```powershell
pip install -r requirements.txt
```

## Running the Application

Run the application with:

```powershell
python app.py
```

## Building Executable

To create an executable (.exe) file:

1. Install PyInstaller (included in requirements.txt):
```powershell
pip install -r requirements.txt
```

2. Build the executable using one of the build scripts:
```powershell
.\build.ps1
```
or
```powershell
.\build.bat
```

Or manually with PyInstaller:
```powershell
pyinstaller --onefile --windowed --name "MinimalPyQtApp" app.py
```

The executable will be created in the `dist` folder.

**PyInstaller options:**
- `--onefile`: Creates a single executable file
- `--windowed`: Hides the console window (no terminal window)
- `--name`: Sets the name of the executable

## Features

- Simple PyQt5 GUI window
- Interactive button that updates the label text