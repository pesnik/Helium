@echo off
REM ============================================
REM Create Self-Signed Certificate for Testing
REM ============================================

echo.
echo ========================================
echo Create Test Certificate for MSIX
echo ========================================
echo.
echo This creates a self-signed certificate for TESTING ONLY.
echo Users will need to install the certificate to trust your app.
echo.
echo For PRODUCTION, get a certificate from a trusted CA.
echo.
pause

REM Create self-signed certificate using PowerShell
echo.
echo Creating self-signed certificate...
echo.

powershell -ExecutionPolicy Bypass -Command "try { $cert = New-SelfSignedCertificate -Type Custom -Subject 'CN=YourCompanyName' -KeyUsage DigitalSignature -FriendlyName 'Helium Test Certificate' -CertStoreLocation 'Cert:\CurrentUser\My' -TextExtension @('2.5.29.37={text}1.3.6.1.5.5.7.3.3', '2.5.29.19={text}'); $pwd = ConvertTo-SecureString -String 'TestPassword123' -Force -AsPlainText; Export-PfxCertificate -Cert $cert -FilePath 'HeliumCert.pfx' -Password $pwd | Out-Null; Export-Certificate -Cert $cert -FilePath 'HeliumCert.cer' -Type CERT | Out-Null; Write-Host 'Certificate created successfully' } catch { Write-Host 'ERROR:' $_.Exception.Message; exit 1 }"

if errorlevel 1 (
    echo.
    echo ========================================
    echo DETAILED ERROR INFORMATION
    echo ========================================
    echo.
    echo The PowerShell command failed. Common causes:
    echo   1. Need to run as Administrator
    echo   2. PowerShell version too old ^(need 5.0+^)
    echo   3. Windows version doesn't support New-SelfSignedCertificate
    echo.
    echo Try running this Command Prompt as Administrator.
    echo.
    pause
    exit /b 1
)

if exist "HeliumCert.pfx" (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Certificate files created:
    echo   - HeliumCert.pfx (for signing - password: TestPassword123)
    echo   - HeliumCert.cer (for users to install)
    echo.
    echo NEXT STEPS:
    echo.
    echo 1. Run build_msix.bat to build and sign your MSIX package
    echo.
    echo 2. To install the app on test machines, users must:
    echo    a. Right-click HeliumCert.cer
    echo    b. Click "Install Certificate"
    echo    c. Choose "Local Machine"
    echo    d. Place in "Trusted Root Certification Authorities"
    echo    e. Then double-click Helium.msix to install
    echo.
    echo 3. For production, replace with a real certificate from:
    echo    - DigiCert, Sectigo, SSL.com, etc.
    echo.
    echo ========================================
) else (
    echo ERROR: Certificate creation failed!
)

echo.
pause
