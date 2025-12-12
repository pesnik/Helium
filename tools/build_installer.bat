@echo off
REM ============================================
REM Build Windows Installer (Inno Setup)
REM ============================================

echo.
echo ========================================
echo Helium - Installer Builder
echo ========================================
echo.
echo This creates a professional Windows installer
echo Installers trigger fewer SmartScreen warnings than bare .exe files
echo.

REM Check if Inno Setup is installed
set "INNO_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"

if "%INNO_PATH%"=="" (
    echo Inno Setup not found!
    echo.
    echo Download and install Inno Setup from:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo After installing, run this script again.
    pause
    exit /b 1
)

echo Found Inno Setup: %INNO_PATH%
echo.

REM Build executable first if needed
if not exist "dist\Helium.exe" (
    echo Building executable first...
    call build.bat
    if errorlevel 1 (
        echo Build failed!
        pause
        exit /b 1
    )
)

echo Creating installer script...
echo.

REM Create Inno Setup script
(
echo [Setup]
echo AppName=Helium Storage Manager
echo AppVersion=2.1.0
echo AppPublisher=Your Company Name
echo AppPublisherURL=https://yourwebsite.com
echo AppSupportURL=https://yourwebsite.com/support
echo AppUpdatesURL=https://yourwebsite.com/downloads
echo DefaultDirName={autopf}\Helium
echo DefaultGroupName=Helium
echo AllowNoIcons=yes
echo OutputDir=installer_output
echo OutputBaseFilename=HeliumSetup-2.1.0
echo Compression=lzma2/max
echo SolidCompression=yes
echo WizardStyle=modern
echo PrivilegesRequired=lowest
echo ArchitecturesInstallIn64BitMode=x64
echo.
echo [Languages]
echo Name: "english"; MessagesFile: "compiler:Default.isl"
echo.
echo [Tasks]
echo Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
echo.
echo [Files]
echo Source: "dist\Helium.exe"; DestDir: "{app}"; Flags: ignoreversion
echo.
echo [Icons]
echo Name: "{group}\Helium"; Filename: "{app}\Helium.exe"
echo Name: "{group}\Uninstall Helium"; Filename: "{uninstallexe}"
echo Name: "{autodesktop}\Helium"; Filename: "{app}\Helium.exe"; Tasks: desktopicon
echo.
echo [Run]
echo Filename: "{app}\Helium.exe"; Description: "{cm:LaunchProgram,Helium}"; Flags: nowait postinstall skipifsilent
) > helium_installer.iss

echo Building installer...
echo.

"%INNO_PATH%" helium_installer.iss

if errorlevel 1 (
    echo Installer build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS!
echo ========================================
echo.

if exist "installer_output\HeliumSetup-2.1.0.exe" (
    echo Installer created: installer_output\HeliumSetup-2.1.0.exe
    for %%I in ("installer_output\HeliumSetup-2.1.0.exe") do echo Size: %%~zI bytes
    echo.
    echo BENEFITS OF USING INSTALLER:
    echo   - More professional appearance
    echo   - Fewer SmartScreen warnings
    echo   - Proper installation/uninstallation
    echo   - Desktop shortcuts
    echo   - Start menu entries
    echo.
    echo NEXT STEPS:
    echo   1. Test the installer on a clean Windows machine
    echo   2. Distribute HeliumSetup-2.1.0.exe instead of Helium.exe
    echo   3. Consider signing the installer for zero warnings
) else (
    echo ERROR: Installer not found!
)

echo.
pause
