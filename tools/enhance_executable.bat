@echo off
REM ============================================
REM Enhance Executable with Reputation Signals
REM No certificate required
REM ============================================

echo.
echo ========================================
echo Helium - Executable Enhancer
echo ========================================
echo.
echo This adds maximum metadata to reduce SmartScreen warnings
echo without requiring a code signing certificate.
echo.

REM Check if rcedit is available (Electron's resource editor)
where rcedit >nul 2>&1
if errorlevel 1 (
    echo [1/3] Downloading rcedit tool...
    echo.

    REM Download rcedit from GitHub
    powershell -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://github.com/electron/rcedit/releases/download/v2.0.0/rcedit-x64.exe' -OutFile 'rcedit.exe'"

    if not exist "rcedit.exe" (
        echo ERROR: Failed to download rcedit
        echo Please download manually from: https://github.com/electron/rcedit/releases
        pause
        exit /b 1
    )

    set "RCEDIT=rcedit.exe"
) else (
    set "RCEDIT=rcedit"
)

echo [2/3] Checking for executable...
echo.

if not exist "dist\Helium.exe" (
    echo ERROR: dist\Helium.exe not found!
    echo Please build the executable first with build.bat or build_nuitka.bat
    pause
    exit /b 1
)

echo [3/3] Adding metadata to executable...
echo.

REM Add comprehensive metadata
"%RCEDIT%" "dist\Helium.exe" ^
    --set-version-string "CompanyName" "Your Company Name" ^
    --set-version-string "FileDescription" "Helium Storage Manager - Organize and manage your files" ^
    --set-version-string "FileVersion" "2.1.0.0" ^
    --set-version-string "InternalName" "Helium" ^
    --set-version-string "LegalCopyright" "Copyright (c) 2025 Your Company Name. All rights reserved." ^
    --set-version-string "OriginalFilename" "Helium.exe" ^
    --set-version-string "ProductName" "Helium Storage Manager" ^
    --set-version-string "ProductVersion" "2.1.0.0" ^
    --set-file-version "2.1.0.0" ^
    --set-product-version "2.1.0.0"

if errorlevel 1 (
    echo ERROR: Failed to add metadata
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS!
echo ========================================
echo.
echo Metadata added to dist\Helium.exe
echo.
echo This helps reduce SmartScreen warnings by:
echo   - Adding professional version info
echo   - Showing company information
echo   - Displaying proper file description
echo.
echo NEXT STEPS for further reputation building:
echo.
echo 1. Distribute consistently from same URL
echo 2. Get users to download and run ^(builds reputation^)
echo 3. Submit to Microsoft for malware scanning
echo 4. Consider VirusTotal upload for multi-AV verification
echo.
echo NOTE: This won't eliminate warnings completely,
echo but reduces their severity. For zero warnings,
echo you need a code signing certificate.
echo.
pause
