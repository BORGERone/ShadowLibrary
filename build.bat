@echo off
chcp 65001 >nul
title Shadow Library - Build

echo.
echo ============================================================
echo   Shadow Library - Сборка в EXE
echo ============================================================
echo.

echo [1/3] Очистка старых сборок...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [2/3] Сборка приложения...
pyinstaller --clean build.spec

echo [3/3] Копирование дополнительных файлов...
if exist "dist\ShadowLibrary" (
    copy "icon.ico" "dist\ShadowLibrary\" >nul 2>&1
    copy "config.json" "dist\ShadowLibrary\" >nul 2>&1
    copy "requirements.txt" "dist\ShadowLibrary\" >nul 2>&1
    echo.
    echo ============================================================
    echo   Сборка завершена!
    echo   EXE файл находится в папке: dist\ShadowLibrary
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo   Ошибка сборки!
    echo ============================================================
)

echo.
pause
