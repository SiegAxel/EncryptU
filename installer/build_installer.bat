@echo off
REM Complete build script for EncryptU - PyInstaller + Installer preparation
echo ================================
echo EncryptU Build Script
echo ================================

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Verify desktop directory exists
if not exist "desktop" (
    echo ERROR: desktop directory not found! Make sure you're running from the project root.
    pause
    exit /b 1
)

REM Step 1: Build executable with PyInstaller
echo.
echo [STEP 1] Building executable with PyInstaller...
python -m PyInstaller --noconfirm --onefile --windowed --name EncryptU --add-data "desktop/controllers/img;controllers/img" desktop/__main__.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)

echo PyInstaller build completed successfully!

REM Step 2: Copy files to installer directory
echo.
echo [STEP 2] Preparing installer files...

REM Create installer output directory
if not exist "installer\installforge\output" mkdir "installer\installforge\output"

REM Copy executable
if exist "dist\EncryptU.exe" (
    copy "dist\EncryptU.exe" "installer\installforge\output\"
    echo - Copied EncryptU.exe
) else (
    echo ERROR: EncryptU.exe not found in dist directory!
    pause
    exit /b 1
)

REM Copy documentation files
if exist "installer\README.txt" (
    copy "installer\README.txt" "installer\installforge\output\"
    echo - Copied README.txt
)

if exist "installer/LICENSE.txt" (
    copy "installer\LICENSE.txt" "installer\installforge\output\"
    echo - Copied LICENSE.txt
)

REM Step 3: Show next steps
echo.
echo ================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ================================
echo.
echo Files prepared for installer:
echo - installer\installforge\output\EncryptU.exe
echo - installer\installforge\output\README.txt
echo - installer\installforge\output\LICENSE.txt
echo.
echo NEXT STEPS:
echo 1. Open InstallForge
echo 2. Create new project using installer/README_InstallForge.md guide
echo 3. Add the files from installer\installforge\output\
echo 4. Build your installer
echo.
echo For detailed instructions, see: installer/README_InstallForge.md
echo.
pause