@echo off
setlocal enabledelayedexpansion

REM ============================================
REM Helium Build System - Main Menu
REM ============================================

:MENU
cls
echo.
echo ========================================
echo    Helium v2.1 - Build System
echo ========================================
echo.
echo  BUILD OPTIONS:
echo  --------------
echo  1. Build with PyInstaller (default)
echo  2. Build with Nuitka (smaller, slower build)
echo  3. Build MSIX Package (Windows Store format)
echo.
echo  DISTRIBUTION OPTIONS:
echo  --------------------
echo  4. Create Portable ZIP (recommended - no download warnings)
echo  5. Create Windows Installer (Inno Setup)
echo.
echo  CERTIFICATE OPTIONS:
echo  -------------------
echo  6. Setup Certificate (convert .pem to .pfx)
echo  7. Create Test Certificate (self-signed)
echo.
echo  INFORMATION:
echo  -----------
echo  8. View distribution options (no certificate)
echo  9. Help / Documentation
echo.
echo  0. Exit
echo.
echo ========================================
echo.

set /p CHOICE="Enter your choice (0-9): "

if "%CHOICE%"=="1" goto BUILD_PYINSTALLER
if "%CHOICE%"=="2" goto BUILD_NUITKA
if "%CHOICE%"=="3" goto BUILD_MSIX
if "%CHOICE%"=="4" goto BUILD_INSTALLER
if "%CHOICE%"=="5" goto BUILD_INSTALLER_INNO
if "%CHOICE%"=="6" goto SETUP_CERT
if "%CHOICE%"=="7" goto CREATE_TEST_CERT
if "%CHOICE%"=="8" goto VIEW_OPTIONS
if "%CHOICE%"=="9" goto HELP
if "%CHOICE%"=="0" goto EXIT

echo Invalid choice! Please try again.
timeout /t 2 >nul
goto MENU

:BUILD_PYINSTALLER
echo.
echo Building with PyInstaller...
call tools\build_pyinstaller.bat
pause
goto MENU

:BUILD_NUITKA
echo.
echo Building with Nuitka...
call tools\build_nuitka.bat
pause
goto MENU

:BUILD_MSIX
echo.
echo Building MSIX Package...
call tools\build_msix.bat
pause
goto MENU

:BUILD_INSTALLER
echo.
echo Creating Portable ZIP...
call tools\create_portable_zip.bat
pause
goto MENU

:BUILD_INSTALLER_INNO
echo.
echo Creating Windows Installer...
call tools\build_installer.bat
pause
goto MENU

:SETUP_CERT
echo.
echo Setting up Certificate...
call tools\setup_certificate.bat
pause
goto MENU

:CREATE_TEST_CERT
echo.
echo Creating Test Certificate...
call tools\create_test_cert.bat
pause
goto MENU

:VIEW_OPTIONS
echo.
echo Opening distribution options guide...
if exist "docs\NO_CERTIFICATE_OPTIONS.md" (
    start "" "docs\NO_CERTIFICATE_OPTIONS.md"
) else (
    echo File not found: docs\NO_CERTIFICATE_OPTIONS.md
)
timeout /t 2 >nul
goto MENU

:HELP
cls
echo.
echo ========================================
echo    Helium Build System - Help
echo ========================================
echo.
echo QUICK START:
echo   1. Choose option 1 to build your executable
echo   2. Find the result in dist\Helium.exe
echo.
echo DISTRIBUTION WITHOUT CERTIFICATE:
echo   - Option 4: Create professional installer
echo   - Option 5: Add metadata to reduce warnings
echo   - Option 8: View all distribution strategies
echo.
echo DISTRIBUTION WITH CERTIFICATE:
echo   - Option 6: If you have .pem files
echo   - Option 7: Create test certificate (testing only)
echo   - Option 3: Build signed MSIX package
echo.
echo DOCUMENTATION:
echo   - docs\MSIX_README.md - MSIX packaging guide
echo   - docs\NO_CERTIFICATE_OPTIONS.md - Distribution without cert
echo   - docs\CERTIFICATE_INFO.md - Certificate types explained
echo   - docs\SECURE_BUILD_GUIDE.md - Secure build process
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:EXIT
echo.
echo Exiting...
exit /b 0
