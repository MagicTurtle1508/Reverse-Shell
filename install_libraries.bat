@echo off
REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)

REM Check if pip is installed
python -m pip --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo pip is not installed. Installing pip...
    python -m ensurepip
)

REM Upgrade pip to the latest version
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install the required libraries
echo Installing required libraries...
python -m pip install -r requirements.txt

REM Compile the Python script to an executable
echo Compiling the Python script...
pyinstaller --onefile your_script.py

echo All libraries installed and script compiled successfully.
pause
