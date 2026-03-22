@echo off
title Shadow Library Build

echo.
echo ============================================================
echo   Shadow Library - Build
echo ============================================================
echo.

echo [1/4] Stopping processes...
taskkill /F /IM ShadowLibrary.exe 2>nul
taskkill /F /IM msedge.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/4] Cleaning old builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [3/4] Building application...
python -m PyInstaller build.spec --noconfirm

echo [4/4] Copying additional files...
if exist "dist\ShadowLibrary.exe" (
    copy "icon.ico" "dist\" >nul 2>&1
    copy "config.json" "dist\" >nul 2>&1
    
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
