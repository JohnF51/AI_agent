@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Nastavenie projektu s uv (Google Antigravity)
echo ==========================================

:: 1. Kontrola, ci je uv uz nainstalovane
where uv >nul 2>nul
if %errorlevel% equ 0 (
    set "UV_CMD=uv"
    echo [OK] Nastroj uv bol najdeny v PATH.
) else (
    if exist "%USERPROFILE%\.local\bin\uv.exe" (
        set "UV_CMD=%USERPROFILE%\.local\bin\uv.exe"
        echo [OK] Nastroj uv bol najdeny v %USERPROFILE%\.local\bin\
    ) else (
        echo [INFO] Nastroj uv nebol najdeny. Instalujem ho cez PowerShell...
        powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
        
        if exist "%USERPROFILE%\.local\bin\uv.exe" (
            set "UV_CMD=%USERPROFILE%\.local\bin\uv.exe"
            echo [OK] Nastroj uv bol uspesne nainstalovany.
        ) else (
            echo [CHYBA] Instalacia uv zlyhala. Prosim nainstalujte uv manualne: pip install uv
            pause
            exit /b 1
        )
    )
)

:: 2. Instalacia Pythonu 3.12
echo.
echo [INFO] Instalujem Python 3.12 cez uv...
"%UV_CMD%" python install 3.12
if %errorlevel% neq 0 (
    echo [CHYBA] Instalacia Pythonu zlyhala.
    pause
    exit /b 1
)

:: 3. Vytvorenie virtualneho prostredia
echo.
echo [INFO] Vytvaram virtualne prostredie (.venv)...
if exist .venv (
    echo [INFO] Virtualne prostredie uz existuje.
) else (
    "%UV_CMD%" venv --python 3.12
    if %errorlevel% neq 0 (
        echo [CHYBA] Vytvorenie venv zlyhalo.
        pause
        exit /b 1
    )
)

:: 4. Instalacia dependencii
echo.
echo [INFO] Instalujem kniznicu google-antigravity z requirements.txt...
"%UV_CMD%" pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [CHYBA] Instalacia balikov zlyhala.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Nastavenie prebehlo USPESNE!
echo Teraz mozes spustit agenta prikazom:
echo uv run main.py
echo ==========================================
pause
