@echo off
REM ============================================
REM Auto-detect and convert PEM certificate
REM ============================================
setlocal enabledelayedexpansion

echo.
echo ========================================
echo Certificate Setup
echo ========================================
echo.

REM Check if OpenSSL is available (comes with Git for Windows)
where openssl >nul 2>&1
if errorlevel 1 (
    echo WARNING: OpenSSL not in PATH!
    echo.
    echo Attempting to use Git's OpenSSL...

    REM Try common Git installation paths
    set "OPENSSL_PATH="
    if exist "C:\Program Files\Git\usr\bin\openssl.exe" set "OPENSSL_PATH=C:\Program Files\Git\usr\bin\openssl.exe"
    if exist "C:\Program Files\Git\mingw64\bin\openssl.exe" set "OPENSSL_PATH=C:\Program Files\Git\mingw64\bin\openssl.exe"
    if exist "%LOCALAPPDATA%\Programs\Git\usr\bin\openssl.exe" set "OPENSSL_PATH=%LOCALAPPDATA%\Programs\Git\usr\bin\openssl.exe"
    if exist "%LOCALAPPDATA%\Programs\Git\mingw64\bin\openssl.exe" set "OPENSSL_PATH=%LOCALAPPDATA%\Programs\Git\mingw64\bin\openssl.exe"

    if "!OPENSSL_PATH!"=="" (
        echo ERROR: OpenSSL not found!
        echo.
        echo OpenSSL is required to convert PEM to PFX format.
        echo.
        echo Install one of:
        echo   1. Git for Windows ^(includes OpenSSL^): https://git-scm.com/
        echo   2. OpenSSL for Windows: https://slproweb.com/products/Win32OpenSSL.html
        echo.
        pause
        exit /b 1
    )

    echo Found OpenSSL at: !OPENSSL_PATH!
    set "OPENSSL_CMD=!OPENSSL_PATH!"
) else (
    set "OPENSSL_CMD=openssl"
)

REM Look for .pem files in root directory
set PEM_COUNT=0
set PEM_FILE=
set KEY_FILE=

echo Scanning for certificate files...
echo.

for %%f in (*.pem) do (
    set /a PEM_COUNT+=1
    set "CURRENT_FILE=%%f"

    REM Check if it's a private key or certificate
    findstr /C:"PRIVATE KEY" "%%f" >nul 2>&1
    if !errorlevel! equ 0 (
        set "KEY_FILE=%%f"
        echo [Found] Private key file
    ) else (
        findstr /C:"CERTIFICATE" "%%f" >nul 2>&1
        if !errorlevel! equ 0 (
            set "PEM_FILE=%%f"
            echo [Found] Certificate file
        )
    )
)

if %PEM_COUNT% equ 0 (
    echo ERROR: No .pem files found in root directory!
    echo.
    echo Please place your certificate files ^(.pem^) in the root directory.
    echo You need:
    echo   - certificate.pem ^(or similar^)
    echo   - private-key.pem ^(or similar^)
    echo.
    pause
    exit /b 1
)

REM Check if we found both certificate and key
if "%PEM_FILE%"=="" (
    echo ERROR: Certificate PEM file not found!
    echo Please ensure you have a certificate.pem file.
    pause
    exit /b 1
)

if "%KEY_FILE%"=="" (
    echo ERROR: Private key PEM file not found!
    echo Please ensure you have a private-key.pem file.
    pause
    exit /b 1
)

echo.
echo Files detected successfully.
echo.

REM Check if PFX already exists
if exist "HeliumCodeSign.pfx" (
    echo HeliumCodeSign.pfx already exists.
    set /p OVERWRITE="Overwrite existing certificate? (y/n): "
    if /i not "!OVERWRITE!"=="y" (
        echo Keeping existing certificate.
        echo.
        pause
        exit /b 0
    )
    del "HeliumCodeSign.pfx"
)

REM Prompt for password
echo.
echo Enter a password to protect your PFX certificate.
echo This password will be needed when signing.
echo.
set /p PFX_PASSWORD="Enter password: "

if "%PFX_PASSWORD%"=="" (
    echo ERROR: Password cannot be empty!
    pause
    exit /b 1
)

echo.
echo Converting PEM to PFX format...
echo.

REM Convert PEM to PFX using OpenSSL
"%OPENSSL_CMD%" pkcs12 -export -out HeliumCodeSign.pfx -inkey "%KEY_FILE%" -in "%PEM_FILE%" -passout pass:%PFX_PASSWORD%

if errorlevel 1 (
    echo.
    echo ERROR: Conversion failed!
    echo Please check your PEM files are valid.
    pause
    exit /b 1
)

if exist "HeliumCodeSign.pfx" (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Certificate converted: HeliumCodeSign.pfx
    echo.
    echo IMPORTANT: Save your password securely!
    echo You'll need it for signing packages.
    echo.
    echo Next steps:
    echo   1. Run build_msix_signed.bat to build and sign MSIX
    echo   2. Keep HeliumCodeSign.pfx file private
    echo   3. Add *.pfx to .gitignore
    echo.
    echo ========================================
) else (
    echo ERROR: PFX file was not created!
)

echo.
pause
