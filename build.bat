@echo off
REM PyInstaller wrapper script - Updated to use python -m PyInstaller
echo ================================
echo EncryptU - Simple Build Script
echo ================================

REM Change to script directory
cd /d "%~dp0"

echo Running PyInstaller build...
python -m PyInstaller --noconfirm --onefile --windowed --name EncryptU --add-data "desktop/controllers/img;controllers/img" desktop/__main__.py

echo.
echo Build completed! Check dist/ directory for the executable.
pause