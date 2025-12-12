@echo off
REM Build with Nuitka (alternative to PyInstaller)

echo.
echo ========================================
echo Helium - Nuitka Build (Less AV flags)
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo Installing Nuitka...
uv pip install nuitka ordered-set zstandard

echo.
echo Building with Nuitka (this takes longer but produces better exe)...
uv run nuitka --standalone --onefile ^
    --windows-console-mode=disable ^
    --enable-plugin=tk-inter ^
    --output-filename=Helium.exe ^
    --company-name="Your Company Name" ^
    --product-name="Helium Storage Manager" ^
    --file-version="2.1.0.0" ^
    --product-version="2.1.0.0" ^
    --file-description="Helium Storage Manager" ^
    --copyright="Copyright (c) 2025" ^
    app.py

if exist "Helium.exe" (
    echo.
    echo Success! Executable: Helium.exe
    for %%I in ("Helium.exe") do echo Size: %%~zI bytes
) else (
    echo Build failed
)

pause
