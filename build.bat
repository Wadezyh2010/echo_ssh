@echo off
REM echo_ssh - Build script for Windows
REM Produces dist\echo_ssh.exe

echo ============================================
echo  echo_ssh - Building standalone exe...
echo ============================================

REM Ensure PyInstaller is installed
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt >nul 2>&1
python -m pip install pyinstaller >nul 2>&1

echo.
echo Running PyInstaller...

pyinstaller --noconfirm --onefile --windowed --name echo_ssh ^
    --hidden-import paramiko ^
    --hidden-import pyte ^
    --hidden-import pyqtgraph ^
    --hidden-import cryptography ^
    --hidden-import bcrypt ^
    --hidden-import pynacl ^
    --hidden-import cffi ^
    --collect-submodules paramiko ^
    --collect-submodules pyte ^
    main.py

echo.
if exist dist\echo_ssh.exe (
    echo ============================================
    echo  Build successful!
    echo  Output: dist\echo_ssh.exe
    echo ============================================
) else (
    echo Build failed. Check the output above.
    exit /b 1
)

pause
