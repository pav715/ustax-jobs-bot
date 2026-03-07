@echo off
title US Tax Jobs - Telegram Bot
color 0A
echo.
echo  =====================================================
echo    US Tax Jobs Telegram Bot
echo    Bot: @USTaxjobs_bot
echo  =====================================================
echo.

cd /d "%~dp0"

echo [1/2] Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Install failed. Check internet connection.
    pause
    exit /b
)

echo [2/2] Starting bot...
echo.
echo  Make sure you have:
echo  1. Added @USTaxjobs_bot as Admin to your Telegram channel
echo  2. Sent any message in the channel
echo.
echo  Press Ctrl+C anytime to stop the bot.
echo.

python bot.py

pause
