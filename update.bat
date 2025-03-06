@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

title Update Tool

echo ================================================
echo              GitHub Update Tool
echo ================================================
echo.

if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: No virtual environment found, using system Python
)

set /p commit_message=Enter commit message (press Enter for default): 
if "!commit_message!"=="" set commit_message=Update project code

set /p force_push=Force push? (y/n, default: n): 
if /i "!force_push!"=="y" (
    set force_arg=force
) else (
    set force_arg=
)

echo.
echo Updating...
python update.py "!commit_message!" !force_arg!

echo.
echo ================================================
echo Press any key to exit...
pause > nul 
