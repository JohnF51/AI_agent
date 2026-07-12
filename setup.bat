@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Project Setup with uv (Google Antigravity)
echo ==========================================

:: 1. Check if uv is installed
where uv >nul 2>nul
if %errorlevel% equ 0 (
    set "UV_CMD=uv"
    echo [OK] uv tool found in PATH.
) else (
    if exist "%USERPROFILE%\.local\bin\uv.exe" (
        set "UV_CMD=%USERPROFILE%\.local\bin\uv.exe"
        echo [OK] uv tool found in %USERPROFILE%\.local\bin\
    ) else (
        echo [INFO] uv tool not found. Installing via PowerShell...
        powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
        
        if exist "%USERPROFILE%\.local\bin\uv.exe" (
            set "UV_CMD=%USERPROFILE%\.local\bin\uv.exe"
            echo [OK] uv tool installed successfully.
        ) else (
            echo [ERROR] Installation of uv failed. Please install uv manually: pip install uv
            pause
            exit /b 1
        )
    )
)

:: 2. Install Python 3.12
echo.
echo [INFO] Installing Python 3.12 via uv...
"%UV_CMD%" python install 3.12
if %errorlevel% neq 0 (
    echo [ERROR] Python installation failed.
    pause
    exit /b 1
)

:: 3. Create virtual environment
echo.
echo [INFO] Creating virtual environment (.venv)...
if exist .venv (
    echo [INFO] Virtual environment already exists.
) else (
    "%UV_CMD%" venv --python 3.12
    if %errorlevel% neq 0 (
        echo [ERROR] Creating venv failed.
        pause
        exit /b 1
    )
)

:: 4. Install dependencies
echo.
echo [INFO] Installing google-antigravity from requirements.txt...
"%UV_CMD%" pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Package installation failed.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Setup completed SUCCESSFULLY!
echo You can now start the agent using:
echo uv run main.py
echo ==========================================
pause
