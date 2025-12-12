@echo off
REM ============================================
REM Submit to Microsoft SmartScreen
REM ============================================

echo.
echo ========================================
echo Submit to Microsoft SmartScreen
echo ========================================
echo.
echo This helps build reputation with Microsoft SmartScreen
echo by proactively submitting your file for analysis.
echo.
echo IMPORTANT: This is a manual process.
echo.
pause

echo.
echo STEP 1: Submit for Analysis
echo ========================================
echo.
echo 1. Go to: https://www.microsoft.com/en-us/wdsi/filesubmission
echo 2. Select "Submit a file for malware analysis"
echo 3. Upload: dist\Helium.exe
echo 4. Provide contact information
echo 5. Select reason: "This is my software that's being flagged"
echo.
echo This tells Microsoft your file is legitimate.
echo.
pause

echo.
echo STEP 2: Submit to VirusTotal
echo ========================================
echo.
echo 1. Go to: https://www.virustotal.com/
echo 2. Upload: dist\Helium.exe
echo 3. Share the results URL with users
echo.
echo This provides transparency and builds trust.
echo Multiple AV vendors will scan and clear your file.
echo.
pause

echo.
echo STEP 3: Build Download Reputation
echo ========================================
echo.
echo SmartScreen tracks:
echo   - How many people download your file
echo   - How many people actually run it
echo   - Whether anyone reports it as malicious
echo.
echo Tips to build reputation:
echo   - Host on consistent URL ^(GitHub Releases, your website^)
echo   - Encourage users to download and run
echo   - After 50-100+ downloads, warnings reduce
echo   - After 500-1000+ downloads, warnings may disappear
echo.
echo This can take 2-4 weeks of consistent downloads.
echo.
pause

echo.
echo STEP 4: Alternative Distribution
echo ========================================
echo.
echo Consider these SmartScreen-free options:
echo.
echo   1. Microsoft Store ^($19 one-time^)
echo      - Zero warnings
echo      - Microsoft signs for you
echo      - Professional distribution
echo.
echo   2. GitHub Releases
echo      - Host your .exe
echo      - Users see it's from GitHub ^(more trusted^)
echo      - Builds reputation over time
echo.
echo   3. Chocolatey Package Manager
echo      - Windows package manager
echo      - Trusted distribution channel
echo      - Users: choco install helium
echo.
pause

echo.
echo ========================================
echo SUMMARY
echo ========================================
echo.
echo Without a code signing certificate, your options are:
echo.
echo   A. Build reputation ^(2-4 weeks, free^)
echo   B. Microsoft Store ^($19, instant^)
echo   C. Buy certificate ^($70-200/year, instant^)
echo.
echo For a professional app, option C ^(certificate^) is recommended.
echo For personal/hobby projects, option B ^(Store^) is best value.
echo.
pause
