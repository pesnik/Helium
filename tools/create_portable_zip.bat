@echo off
REM ============================================
REM Create Portable ZIP Package
REM ============================================

cd /d "%~dp0\.."

echo.
echo ========================================
echo Helium - Portable ZIP Creator
echo ========================================
echo.

REM Check if executable exists
if not exist "dist\Helium.exe" (
    echo ERROR: dist\Helium.exe not found!
    echo Please build the executable first with build.bat
    pause
    exit /b 1
)

echo Creating portable ZIP package...
echo.

REM Create release folder structure
if exist "release" rmdir /s /q "release"
mkdir "release\Helium-Portable"

REM Copy executable
echo [1/4] Copying executable...
copy "dist\Helium.exe" "release\Helium-Portable\" >nul

REM Create README
echo [2/4] Creating README...
(
echo Helium Storage Manager v2.1 - Portable Edition
echo =============================================
echo.
echo INSTALLATION:
echo   1. Extract this folder anywhere on your computer
echo   2. Double-click Helium.exe to run
echo   3. No installation required!
echo.
echo FIRST RUN:
echo   If Windows shows a security warning:
echo   - Click "More info"
echo   - Click "Run anyway"
echo   This only happens on first run.
echo.
echo UNINSTALLATION:
echo   Simply delete this folder - no traces left behind.
echo.
echo PORTABLE MODE:
echo   All your data is stored in this folder.
echo   You can copy this folder to a USB drive and run from there.
echo.
echo Support: https://github.com/yourusername/helium
echo.
echo Copyright ^(c^) 2025 Your Company Name
) > "release\Helium-Portable\README.txt"

REM Create version info
echo [3/4] Creating version info...
(
echo Helium Storage Manager
echo Version: 2.1.0
echo Build Date: %DATE%
echo.
echo This is a portable version - no installation required.
) > "release\Helium-Portable\VERSION.txt"

echo [4/4] Creating ZIP archive...

REM Use PowerShell to create ZIP (built into Windows 10+)
powershell -Command "Compress-Archive -Path 'release\Helium-Portable\*' -DestinationPath 'Helium-v2.1-Portable.zip' -Force"

if exist "Helium-v2.1-Portable.zip" (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Portable ZIP created: Helium-v2.1-Portable.zip
    for %%I in ("Helium-v2.1-Portable.zip") do echo Size: %%~zI bytes
    echo.
    echo BENEFITS OF ZIP DISTRIBUTION:
    echo   - No SmartScreen warnings when downloading
    echo   - Users extract and run - more trusted
    echo   - Includes helpful README
    echo   - Professional appearance
    echo.
    echo DISTRIBUTE THIS FILE:
    echo   - Upload to your website
    echo   - Share via GitHub Releases
    echo   - Send to users directly
    echo.
    echo Users will see Windows SmartScreen only when they RUN
    echo the exe after extraction, not during download.
    echo.
) else (
    echo ERROR: Failed to create ZIP file!
)

echo ========================================
pause
