# MSIX Packaging Guide for Helium

## What is MSIX?

MSIX is Microsoft's modern app packaging format that provides:
- ✅ **No SmartScreen warnings** when properly signed
- ✅ Clean installation and uninstallation
- ✅ Automatic updates support
- ✅ Can be distributed via Microsoft Store or side-loaded
- ✅ Better security through sandboxing

## Quick Start

### For Testing (Self-Signed Certificate)

1. **Create a test certificate:**
   ```batch
   create_test_cert.bat
   ```
   This creates `HeliumCert.pfx` and `HeliumCert.cer`

2. **Build the MSIX package:**
   ```batch
   build_msix.bat
   ```
   This creates `Helium.msix`

3. **Install on test machine:**
   - First, install the certificate:
     - Right-click `HeliumCert.cer` → Install Certificate
     - Choose "Local Machine" (requires admin)
     - Select "Place all certificates in the following store"
     - Browse → "Trusted Root Certification Authorities"
   - Then double-click `Helium.msix` to install the app

### For Production (Trusted Certificate)

1. **Get a code signing certificate** from a trusted Certificate Authority:
   - **Sectigo** (~$70/year) - Budget option
   - **DigiCert** (~$200/year) - Industry standard
   - **SSL.com** (~$100/year) - Good middle ground

2. **Update AppxManifest.xml** with your certificate info:
   ```xml
   <Identity Name="Helium.StorageManager"
             Publisher="CN=Your Actual Company Name"
             Version="2.1.0.0" />
   ```
   The Publisher field must match your certificate's CN (Common Name)

3. **Build and sign:**
   ```batch
   build_msix.bat
   ```
   Or manually sign:
   ```batch
   signtool sign /fd SHA256 /f YourCert.pfx /p YourPassword Helium.msix
   ```

## Distribution Options

### Option 1: Side-Loading (Direct Distribution)

**Pros:**
- Full control over distribution
- No store fees
- Immediate updates

**Cons:**
- Still need a trusted certificate ($70-200/year)
- Users install from .msix file

**Distribution:**
- Upload `Helium.msix` to your website
- Users download and double-click to install
- No SmartScreen warnings with proper certificate!

### Option 2: Microsoft Store

**Pros:**
- No certificate needed (Microsoft signs for you)
- Automatic updates
- Built-in discovery
- Highest trust level

**Cons:**
- $19 one-time developer account fee
- Review process (usually 24-48 hours)
- Microsoft takes 15% cut if charging for app

**Steps:**
1. Create Microsoft Partner Center account ($19)
2. Submit app for review
3. Once approved, users install from Microsoft Store

### Option 3: Microsoft Store for Business (Private Distribution)

**Pros:**
- Distribute privately to your organization
- No public listing needed
- Free for businesses

**Cons:**
- Only for organizations with enterprise accounts

## File Structure

```
Helium/
├── AppxManifest.xml          # Package manifest
├── build_msix.bat            # Build script
├── create_test_cert.bat      # Test certificate generator
├── HeliumCert.pfx           # Your signing certificate (don't commit!)
├── HeliumCert.cer           # Public certificate (for testing)
└── msix_package/            # Generated during build
    ├── Helium.exe
    ├── AppxManifest.xml
    └── Assets/
        ├── Square150x150Logo.png
        ├── Square44x44Logo.png
        └── StoreLogo.png
```

## Customization

### 1. Update Company Information

Edit `AppxManifest.xml`:
```xml
<Identity Name="Helium.StorageManager"
          Publisher="CN=YourActualCompanyName"
          Version="2.1.0.0" />

<Properties>
  <DisplayName>Helium Storage Manager</DisplayName>
  <PublisherDisplayName>Your Company Name</PublisherDisplayName>
</Properties>
```

### 2. Add Real Logo Images

Replace placeholder images in `msix_package/Assets/`:
- **Square150x150Logo.png** - 150x150px (Start menu tile)
- **Square44x44Logo.png** - 44x44px (App list icon)
- **StoreLogo.png** - 50x50px (Store listing)

### 3. Update Version Number

In `AppxManifest.xml`, update:
```xml
<Identity Version="2.1.0.0" />
```

Version must be in format: Major.Minor.Build.Revision

## Troubleshooting

### "makeappx is not recognized"

Install Windows SDK:
- Download: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
- Or add to PATH: `C:\Program Files (x86)\Windows Kits\10\bin\10.0.XXXXX.0\x64`

### "Package could not be opened"

The package needs to be signed. Run `create_test_cert.bat` first.

### "App installation failed - certificate not trusted"

Install the `.cer` file to Trusted Root Certification Authorities first.

### "Publisher does not match"

The Publisher in `AppxManifest.xml` must exactly match your certificate's Common Name (CN).

## Cost Comparison

| Method | Initial Cost | Annual Cost | SmartScreen Warnings |
|--------|--------------|-------------|---------------------|
| No signing | $0 | $0 | ⚠️ Always warns |
| Self-signed MSIX | $0 | $0 | ⚠️ Warns (need cert install) |
| Trusted cert + MSIX | $70-200 | $70-200 | ✅ No warnings |
| Microsoft Store | $19 | $0 | ✅ No warnings |

## Recommendation

**For hobbyist/personal projects:**
- Use self-signed MSIX for testing
- Publish to Microsoft Store for free distribution ($19 one-time)

**For commercial/professional projects:**
- Get a code signing certificate ($70-200/year)
- Side-load MSIX files OR publish to Store
- Professional appearance, no warnings

**For enterprise/internal tools:**
- Self-signed MSIX with IT department installing certificate
- Or use Microsoft Store for Business

## Additional Resources

- [MSIX Documentation](https://docs.microsoft.com/en-us/windows/msix/)
- [Windows SDK Download](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/)
- [Microsoft Partner Center](https://partner.microsoft.com/)
- [Code Signing Certificates](https://www.ssl.com/code-signing/)
