@echo off
chcp 65001 >nul
title OneKey BORGER Version - Web Server

echo.
echo ============================================================
echo   OneKey BORGER Version - Web Server
echo ============================================================
echo.
echo  Запуск веб-сервера...
echo  Откройте в браузере: http://localhost:8000
echo  http://127.0.0.1:8000
echo.
echo  Нажмите Ctrl+C для остановки сервера
echo.

python web_server.py

pause
