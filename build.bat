@echo off
REM ============================================
REM Helium Storage Manager - Quick Build
REM ============================================
REM
REM This is the quick build script.
REM For more options, run: build_menu.bat
REM ============================================

echo.
echo Quick building with PyInstaller...
echo For more build options, run: build_menu.bat
echo.

call tools\build_pyinstaller.bat

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

pause
