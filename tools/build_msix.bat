@echo off
REM ============================================
REM Helium Storage Manager - MSIX Package Builder
REM ============================================

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
    echo WARNING: signtool not found!
    echo Package will be created but not signed.
    echo Install Windows SDK for signing capability.
    echo.
)

echo [1/5] Building executable first...
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
echo [2/5] Preparing MSIX package structure...

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

echo [3/5] Creating placeholder assets...
echo (You should replace these with real PNG images)

REM Create placeholder assets using PowerShell
powershell -Command "Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap(150,150); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::Blue); $g.DrawString('Helium', (New-Object System.Drawing.Font('Arial',20)), [System.Drawing.Brushes]::White, 10, 60); $bmp.Save('msix_package\Assets\Square150x150Logo.png'); $bmp.Dispose(); $g.Dispose()"

powershell -Command "Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap(44,44); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::Blue); $bmp.Save('msix_package\Assets\Square44x44Logo.png'); $bmp.Dispose(); $g.Dispose()"

powershell -Command "Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap(50,50); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::Blue); $bmp.Save('msix_package\Assets\StoreLogo.png'); $bmp.Dispose(); $g.Dispose()"

echo.
echo [4/5] Creating MSIX package...

REM Create the MSIX package
makeappx pack /d "msix_package" /p "Helium.msix" /o
if errorlevel 1 (
    echo ERROR: Failed to create MSIX package!
    pause
    exit /b 1
)

echo.
echo [5/5] Signing package...

REM Check if certificate exists
if exist "HeliumCert.pfx" (
    echo Signing with existing certificate...
    signtool sign /fd SHA256 /a /f "HeliumCert.pfx" "Helium.msix"
    if errorlevel 1 (
        echo WARNING: Signing failed, but package was created.
        echo The unsigned package can still be used for testing.
    ) else (
        echo Package signed successfully!
    )
) else (
    echo.
    echo ========================================
    echo CERTIFICATE NOT FOUND
    echo ========================================
    echo.
    echo To create a self-signed certificate for testing, run:
    echo.
    echo   create_test_cert.bat
    echo.
    echo For production, you need a trusted code signing certificate.
    echo.
    echo The unsigned MSIX package has been created but cannot be
    echo installed without a certificate.
    echo ========================================
)

echo.
echo ========================================
echo MSIX PACKAGE BUILD COMPLETE!
echo ========================================
echo.

if exist "Helium.msix" (
    echo Package created: Helium.msix
    for %%I in ("Helium.msix") do echo Size: %%~zI bytes
    echo.
    echo NEXT STEPS:
    echo 1. For testing: Create a test certificate with create_test_cert.bat
    echo 2. For production: Get a code signing certificate from a CA
    echo 3. Sign the package with: signtool sign /fd SHA256 /f cert.pfx Helium.msix
    echo 4. Users install by double-clicking Helium.msix
) else (
    echo ERROR: Package file not created!
)

echo.
echo ========================================
pause
