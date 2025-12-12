@echo off
REM ============================================
REM Helium Storage Manager - MSIX Package Builder
REM With Automatic Certificate Detection
REM ============================================
setlocal enabledelayedexpansion

echo.
echo ========================================
echo Helium v2.1 - MSIX Package Builder
echo ========================================
echo.

REM Check if makeappx is available (comes with Windows SDK)
where makeappx >nul 2>&1
if errorlevel 1 (
    echo ERROR: makeappx not found!
    echo.
    echo You need to install Windows SDK.
    echo Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
    echo.
    echo Or add Windows SDK bin folder to PATH:
    echo Example: C:\Program Files ^(x86^)\Windows Kits\10\bin\10.0.22621.0\x64
    pause
    exit /b 1
)

REM Check if signtool is available
where signtool >nul 2>&1
if errorlevel 1 (
    echo ERROR: signtool not found!
    echo.
    echo You need to install Windows SDK.
    echo Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
    pause
    exit /b 1
)

echo [1/6] Building executable first...
echo.

REM Build with PyInstaller or Nuitka first
if exist "build.bat" (
    call build.bat
    if errorlevel 1 (
        echo ERROR: Executable build failed!
        pause
        exit /b 1
    )
) else (
    echo ERROR: build.bat not found!
    pause
    exit /b 1
)

echo.
echo [2/6] Preparing MSIX package structure...

REM Create MSIX package directory structure
if exist "msix_package" rmdir /s /q "msix_package"
mkdir "msix_package"
mkdir "msix_package\Assets"

REM Copy executable
if exist "dist\Helium.exe" (
    echo Copying Helium.exe...
    copy "dist\Helium.exe" "msix_package\" >nul
) else (
    echo ERROR: Helium.exe not found in dist folder!
    pause
    exit /b 1
)

REM Copy manifest
if exist "AppxManifest.xml" (
    echo Copying AppxManifest.xml...
    copy "AppxManifest.xml" "msix_package\" >nul
) else (
    echo ERROR: AppxManifest.xml not found!
    pause
    exit /b 1
)

echo [3/6] Creating placeholder assets...
echo (Replace these with real PNG images for production)
echo.

REM Create placeholder assets using PowerShell (silently)
powershell -Command "Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap(150,150); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::Blue); $g.DrawString('Helium', (New-Object System.Drawing.Font('Arial',20)), [System.Drawing.Brushes]::White, 10, 60); $bmp.Save('msix_package\Assets\Square150x150Logo.png'); $bmp.Dispose(); $g.Dispose()" 2>nul

powershell -Command "Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap(44,44); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::Blue); $bmp.Save('msix_package\Assets\Square44x44Logo.png'); $bmp.Dispose(); $g.Dispose()" 2>nul

powershell -Command "Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap(50,50); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::Blue); $bmp.Save('msix_package\Assets\StoreLogo.png'); $bmp.Dispose(); $g.Dispose()" 2>nul

echo [4/6] Creating MSIX package...
echo.

REM Create the MSIX package
makeappx pack /d "msix_package" /p "Helium.msix" /o >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to create MSIX package!
    makeappx pack /d "msix_package" /p "Helium.msix" /o
    pause
    exit /b 1
)

echo Package created successfully.
echo.

echo [5/6] Detecting certificate...
echo.

REM Auto-detect PFX file
set PFX_FILE=
set PFX_COUNT=0

for %%f in (*.pfx) do (
    set /a PFX_COUNT+=1
    set "PFX_FILE=%%f"
)

if %PFX_COUNT% equ 0 (
    echo ========================================
    echo NO CERTIFICATE FOUND
    echo ========================================
    echo.
    echo No .pfx certificate file found in root directory.
    echo.
    echo Options:
    echo   1. If you have .pem files, run: setup_certificate.bat
    echo   2. For testing, run: create_test_cert.bat
    echo   3. For production, obtain a code signing certificate
    echo.
    echo The unsigned MSIX package has been created but cannot be
    echo installed without signing.
    echo.
    pause
    exit /b 1
)

if %PFX_COUNT% gtr 1 (
    echo WARNING: Multiple PFX files found. Using the first one.
    echo.
)

echo Certificate file detected.
echo.

echo [6/6] Signing package...
echo.

REM Prompt for password securely
set /p PFX_PASSWORD="Enter certificate password: "

if "%PFX_PASSWORD%"=="" (
    echo ERROR: Password cannot be empty!
    pause
    exit /b 1
)

REM Sign the package
signtool sign /fd SHA256 /f "%PFX_FILE%" /p %PFX_PASSWORD% /tr http://timestamp.digicert.com /td sha256 "Helium.msix" >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Signing failed!
    echo.
    echo Possible reasons:
    echo   1. Incorrect password
    echo   2. Invalid certificate
    echo   3. Certificate expired
    echo.
    echo Trying again with verbose output...
    echo.
    signtool sign /fd SHA256 /f "%PFX_FILE%" /p %PFX_PASSWORD% /tr http://timestamp.digicert.com /td sha256 "Helium.msix"
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.

if exist "Helium.msix" (
    echo Package: Helium.msix
    for %%I in ("Helium.msix") do echo Size: %%~zI bytes
    echo Status: Signed and ready for distribution
    echo.
    echo DISTRIBUTION:
    echo   - Users can install by double-clicking Helium.msix
    echo   - No SmartScreen warnings (if using trusted certificate)
    echo   - Clean installation and uninstallation
    echo.
    echo NEXT STEPS:
    echo   1. Test installation on a clean Windows machine
    echo   2. Distribute Helium.msix to users
    echo   3. Consider publishing to Microsoft Store
) else (
    echo ERROR: Package file not created!
)

echo.
echo ========================================
pause
