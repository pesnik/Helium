@echo off
REM ============================================
REM PyInstaller Build Module
REM ============================================

cd /d "%~dp0\.."

echo.
echo ========================================
echo Helium v2.1 - PyInstaller Build
echo ========================================
echo.
echo NOTE: If build fails with "Access Denied" error:
echo   - Run as Administrator, OR
echo   - Add antivirus exception for this folder
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

REM Install required packages
echo [2/4] Installing PyInstaller...
pip uninstall typing -y >nul 2>&1
pip install pyinstaller

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install PyInstaller!
    echo.
    echo Please try manually:
    echo   pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo PyInstaller installed successfully.
echo.

REM Clean previous build
echo [3/4] Cleaning previous build files...
if exist "dist" (
    echo Removing dist folder...
    rmdir /s /q "dist" 2>nul
    timeout /t 1 >nul
)
if exist "build" (
    echo Removing build folder...
    rmdir /s /q "build" 2>nul
    timeout /t 1 >nul
)
echo Previous build files cleaned.
echo.

REM Determine PyInstaller command
set "PYINSTALLER_CMD=pyinstaller"
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not in PATH, using python -m PyInstaller instead...
    set "PYINSTALLER_CMD=python -m PyInstaller"
)

REM Build the executable
echo [4/4] Building Helium executable...
echo This may take a few minutes...
echo.

REM Check if custom spec file exists, otherwise use default build
if exist "Helium.spec" (
    echo Using custom spec file: Helium.spec
    %PYINSTALLER_CMD% --clean --noconfirm Helium.spec
) else (
    echo Using default PyInstaller settings...

    REM Try with version file if it exists
    if exist "version_info.txt" (
        echo Including version metadata from version_info.txt
        %PYINSTALLER_CMD% --onefile --windowed ^
            --name "Helium" ^
            --noconsole ^
            --clean ^
            --noconfirm ^
            --version-file "version_info.txt" ^
            app.py
    ) else (
        echo Building without version metadata
        %PYINSTALLER_CMD% --onefile --windowed ^
            --name "Helium" ^
            --noconsole ^
            --clean ^
            --noconfirm ^
            app.py
    )
)

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    exit /b 1
)

echo.
echo Verifying build...
if exist "dist\Helium.exe" (
    echo Build verification successful!
    for %%I in ("dist\Helium.exe") do echo Executable size: %%~zI bytes
) else (
    echo WARNING: Helium.exe not found in dist folder!
)

echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo The executable is located at: dist\Helium.exe
echo.
echo You can now distribute the entire 'dist' folder
echo as a portable application.
echo.
echo ========================================
