@echo off
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%.venv"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "REQUIREMENTS=%PROJECT_DIR%requirements.txt"
set "MAIN_SCRIPT=%PROJECT_DIR%main.py"
set "APP_NAME=Lazy Integration"

if not exist "%VENV_DIR%" (
    echo [1/4] Creating virtual environment...
    py -3 -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERROR: Failed to create venv. Make sure Python 3 is installed.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual environment found
)

echo [2/4] Installing dependencies...
"%PYTHON%" -m pip install -r "%REQUIREMENTS%" -q
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo [3/4] Cleaning previous build...
if exist "%PROJECT_DIR%dist\." rmdir /s /q "%PROJECT_DIR%dist"
if exist "%PROJECT_DIR%build\." rmdir /s /q "%PROJECT_DIR%build"
if exist "%PROJECT_DIR%%APP_NAME%.spec" del /q "%PROJECT_DIR%%APP_NAME%.spec"

echo [4/4] Building executable...
"%PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed --name "%APP_NAME%" --icon "%PROJECT_DIR%app.ico" --add-data "%PROJECT_DIR%templates;templates" --add-data "%PROJECT_DIR%logs;logs" "%MAIN_SCRIPT%"

if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo Build complete.
echo Executable: %PROJECT_DIR%dist\%APP_NAME%.exe
pause
