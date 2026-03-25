@echo off
title Shadow Library Build

echo.
echo ============================================================
echo   Shadow Library - Build
echo ============================================================
echo.

echo [1/5] Stopping processes...
taskkill /F /IM ShadowLibrary.exe 2>nul
taskkill /F /IM msedge.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/5] Cleaning old builds and cache...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "common\__pycache__" rmdir /s /q "common\__pycache__"
if exist "templates\__pycache__" rmdir /s /q "templates\__pycache__"
if exist "locales\__pycache__" rmdir /s /q "locales\__pycache__"
for /d %%i in ("%TEMP%\_MEI*") do rmdir /s /q "%%i" 2>nul

echo [3/5] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [4/5] Building application...
python -m PyInstaller build.spec --noconfirm

echo [5/5] Build complete...
if exist "dist\ShadowLibrary.exe" (
    echo.
    echo ============================================================
    echo   Build completed successfully!
    echo ============================================================
    echo.
    echo   EXE file: dist\ShadowLibrary.exe
    echo.
    echo   To test run: dist\ShadowLibrary.exe
    echo.
) else (
    echo.
    echo ============================================================
    echo   ERROR: ShadowLibrary.exe not found!
    echo ============================================================
)

pause
