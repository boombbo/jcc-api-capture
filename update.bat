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

echo.
echo Updating...
python update.py "!commit_message!"

echo.
echo ================================================
echo Press any key to exit...
pause > nul 
