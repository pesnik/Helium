# Secure Certificate Build Guide

## Overview

This guide shows how to use your private `.pem` certificate files securely without exposing the filenames in code or version control.

## Security Features

✅ **Auto-detection** - Scripts automatically find `.pem` files without hardcoding names
✅ **Git protection** - All certificate files are in `.gitignore`
✅ **No filename exposure** - Scripts never display or log certificate filenames
✅ **Password protected** - PFX files require password for signing

## Setup Process

### Step 1: Place Your Certificate Files

Put your `.pem` files in the root directory (`d:\Helium\`):
- `your-certificate-name.pem` (certificate file)
- `your-private-key-name.pem` (private key file)

**The actual filenames don't matter** - the script will find them automatically.

### Step 2: Convert PEM to PFX

Run the setup script:
```batch
setup_certificate.bat
```

This will:
1. Automatically detect your `.pem` files
2. Ask you to set a password
3. Convert to `HeliumCodeSign.pfx`
4. Never display or log your `.pem` filenames

**Enter a strong password and save it securely!**

### Step 3: Build Signed MSIX Package

Run the build script:
```batch
build_msix_signed.bat
```

This will:
1. Build your executable (`build.bat`)
2. Create MSIX package
3. Auto-detect the `.pfx` certificate
4. Ask for your password
5. Sign the package
6. Create `Helium.msix` (ready for distribution)

## File Security

### Protected Files (Never Committed)

The following are in `.gitignore`:
```
*.pem          # Your original certificates
*.pfx          # Converted certificate
*.p12          # Alternative PFX format
*.key          # Private keys
*.cer          # Public certificates
HeliumCodeSign.*  # Any HeliumCodeSign files
msix_package/  # Build artifacts
*.msix         # Final packages
```

### What Gets Committed

Only these safe files are tracked:
```
✅ build.bat                  # Build scripts
✅ build_msix_signed.bat     # MSIX builder
✅ setup_certificate.bat     # Certificate converter
✅ AppxManifest.xml          # MSIX manifest
✅ .gitignore                # Protection rules
```

## Workflow

### First Time Setup
```batch
# 1. Place your .pem files in root (any filename)
# 2. Convert to PFX
setup_certificate.bat

# 3. Build signed MSIX
build_msix_signed.bat
```

### Subsequent Builds
```batch
# Just run the build script
build_msix_signed.bat
```

The PFX file persists, so you only need to run `setup_certificate.bat` once.

## How Auto-Detection Works

### setup_certificate.bat
```batch
# Scans for *.pem files
# Identifies which is certificate vs private key
# Never displays filenames
# Converts to standard HeliumCodeSign.pfx
```

### build_msix_signed.bat
```batch
# Scans for *.pfx files
# Uses first one found
# Never displays filename
# Prompts for password
# Signs the package
```

## Password Management

**DO NOT** hardcode passwords in batch files!

**Good practices:**
- Store password in password manager (1Password, Bitwarden, etc.)
- Enter manually when prompted
- For CI/CD, use environment variables or secrets management

**Bad practices:**
- ❌ `set PASSWORD=mypassword123` in batch file
- ❌ Committing password to git
- ❌ Sharing password in plain text

## Production Checklist

Before distributing:

- [ ] Certificate files (`.pem`, `.pfx`) are in `.gitignore`
- [ ] No passwords in code or committed files
- [ ] Using a **trusted** code signing certificate (not self-signed)
- [ ] Updated `AppxManifest.xml` with your company name
- [ ] Tested installation on clean Windows machine
- [ ] Verified no SmartScreen warnings
- [ ] Package is signed (verify with: `signtool verify /pa Helium.msix`)

## Verify Signature

To check if your MSIX is properly signed:

```batch
signtool verify /pa Helium.msix
```

Should show:
```
Successfully verified: Helium.msix
```

## Troubleshooting

### "No .pem files found"
- Ensure `.pem` files are in root directory (not subdirectories)
- Files must have `.pem` extension

### "OpenSSL not found"
- Install Git for Windows (includes OpenSSL)
- Or download OpenSSL: https://slproweb.com/products/Win32OpenSSL.html

### "Signing failed"
- Check password is correct
- Verify certificate hasn't expired
- Ensure certificate is for code signing (not SSL)

### "makeappx not found"
- Install Windows SDK
- Download: https://developer.microsoft.com/windows/downloads/windows-sdk/

## Certificate Types

### Self-Signed (Testing Only)
```batch
create_test_cert.bat
```
- Free
- Users must install certificate manually
- Not for public distribution

### Trusted Certificate (Production)
Buy from:
- **Sectigo** (~$70/year) - Budget option
- **SSL.com** (~$100/year) - Good value
- **DigiCert** (~$200/year) - Premium

Order as `.pem` or `.pfx` format.

## Distribution

Once you have `Helium.msix`:

1. **Upload to your website/GitHub releases**
2. **Users download and double-click to install**
3. **No warnings** (if signed with trusted certificate)

Or:

1. **Submit to Microsoft Store** ($19 one-time)
2. **Microsoft signs for you** (no certificate needed)
3. **Automatic updates** for users

## Quick Reference

| Command | Purpose |
|---------|---------|
| `setup_certificate.bat` | Convert `.pem` to `.pfx` (first time) |
| `build_msix_signed.bat` | Build and sign MSIX package |
| `create_test_cert.bat` | Create self-signed cert (testing) |

## Support

For more details:
- [MSIX_README.md](MSIX_README.md) - MSIX packaging guide
- [CERTIFICATE_INFO.md](CERTIFICATE_INFO.md) - Certificate types explained
