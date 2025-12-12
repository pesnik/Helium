# Helium Build System

## Quick Start

### Simple Build (Recommended)
```batch
build.bat
```
Builds with PyInstaller (default). Output: `dist\Helium.exe`

### Full Build Menu
```batch
build_menu.bat
```
Interactive menu with all build and distribution options.

---

## File Structure

```
Helium/
├── build.bat                 # Quick build (PyInstaller)
├── build_menu.bat           # Interactive menu (all options)
│
├── tools/                   # Build tools (modular scripts)
│   ├── build_pyinstaller.bat    # PyInstaller build
│   ├── build_nuitka.bat         # Nuitka build
│   ├── build_msix.bat           # MSIX package
│   ├── build_msix_signed.bat    # Signed MSIX
│   ├── build_installer.bat      # Windows installer
│   ├── enhance_executable.bat   # Add metadata
│   ├── setup_certificate.bat    # Convert .pem to .pfx
│   ├── create_test_cert.bat     # Test certificate
│   └── submit_to_microsoft.bat  # Reputation guide
│
└── docs/                    # Documentation
    ├── NO_CERTIFICATE_OPTIONS.md    # Distribution without cert
    ├── MSIX_README.md               # MSIX packaging guide
    ├── CERTIFICATE_INFO.md          # Certificate types
    └── SECURE_BUILD_GUIDE.md        # Secure build process
```

---

## Build Options

### 1. PyInstaller (Default)
```batch
build.bat
```
- **Fast build**
- **Good compatibility**
- Output: `dist\Helium.exe`

### 2. Nuitka
```batch
build_menu.bat → Option 2
```
- **Smaller executable**
- **Slower build time**
- **Better optimization**

### 3. MSIX Package
```batch
build_menu.bat → Option 3
```
- **Windows Store format**
- **Professional installation**
- **Requires Windows SDK**

---

## Distribution Options

### Without Certificate (Free)

#### Option A: Windows Installer
```batch
build_menu.bat → Option 4
```
- Creates professional installer
- Reduces SmartScreen warnings by ~30-50%
- Requires: Inno Setup

#### Option B: Enhanced Metadata
```batch
build_menu.bat → Option 5
```
- Adds version info and metadata
- Minor warning reduction (~10%)
- No extra tools needed

#### Option C: Microsoft Store ($19)
- Build MSIX package (Option 3)
- Submit to Microsoft Store
- **Zero SmartScreen warnings**
- Best value for money

### With Certificate (Paid)

#### Option D: Code Signing
```batch
# If you have .pem files:
build_menu.bat → Option 6

# Then build signed MSIX:
build_menu.bat → Option 3
```
- **Cost:** $70-200/year
- **Result:** Zero warnings (after reputation building)

---

## Menu System Usage

### Interactive Menu
```batch
build_menu.bat
```

Menu Options:
```
1. Build with PyInstaller      → dist\Helium.exe
2. Build with Nuitka           → Helium.exe
3. Build MSIX Package          → Helium.msix
4. Create Windows Installer    → HeliumSetup-2.1.0.exe
5. Enhance Executable          → Adds metadata to existing .exe
6. Setup Certificate           → Convert .pem to .pfx
7. Create Test Certificate     → Self-signed (testing only)
8. View distribution options   → Opens guide
9. Help / Documentation        → Shows help
0. Exit
```

---

## Common Workflows

### First Time Setup
```batch
# 1. Build executable
build.bat

# 2. Test it
dist\Helium.exe

# 3. For distribution, choose one:

# Option A: Create installer (free)
build_menu.bat → Option 4

# Option B: Enhance metadata (free)
build_menu.bat → Option 5

# Option C: Publish to Store ($19)
build_menu.bat → Option 3 → Submit to Store
```

### Development Workflow
```batch
# Quick rebuild during development
build.bat

# Full rebuild with all options
build_menu.bat → Option 1
```

### Production Release
```batch
# 1. Build with version info
build.bat

# 2. Create installer
build_menu.bat → Option 4

# 3. Optionally sign
build_menu.bat → Option 6  # If you have certificate
```

---

## Output Locations

| Build Type | Output Location |
|------------|----------------|
| PyInstaller | `dist\Helium.exe` |
| Nuitka | `Helium.exe` (root) |
| MSIX | `Helium.msix` (root) |
| Installer | `installer_output\HeliumSetup-2.1.0.exe` |

---

## Documentation

- **[NO_CERTIFICATE_OPTIONS.md](docs/NO_CERTIFICATE_OPTIONS.md)** - Complete guide to distribution without certificates
- **[MSIX_README.md](docs/MSIX_README.md)** - MSIX packaging detailed guide
- **[CERTIFICATE_INFO.md](docs/CERTIFICATE_INFO.md)** - Certificate types and formats
- **[SECURE_BUILD_GUIDE.md](docs/SECURE_BUILD_GUIDE.md)** - Secure build with certificates

---

## Troubleshooting

### Build fails
- Check Python is installed: `python --version`
- Install dependencies: `pip install pyinstaller`

### Menu doesn't show options
- Run from Command Prompt, not PowerShell
- Or use: `cmd /c build_menu.bat`

### Tools not found
- Make sure you're running from the root `Helium\` directory
- Scripts expect `tools\` subfolder to exist

---

## Quick Reference

| Task | Command |
|------|---------|
| Quick build | `build.bat` |
| Full menu | `build_menu.bat` |
| PyInstaller | `tools\build_pyinstaller.bat` |
| Nuitka | `tools\build_nuitka.bat` |
| MSIX | `tools\build_msix.bat` |
| Installer | `tools\build_installer.bat` |
| Add metadata | `tools\enhance_executable.bat` |
| Setup cert | `tools\setup_certificate.bat` |

---

## Recommended Approach

**For hobbyist/personal projects:**
```batch
1. build.bat
2. build_menu.bat → Option 4 (Installer)
3. Distribute HeliumSetup-2.1.0.exe
```

**For commercial/professional:**
```batch
1. Get code signing certificate
2. build_menu.bat → Option 6 (Setup cert)
3. build_menu.bat → Option 3 (Build MSIX)
4. Distribute Helium.msix
```

**For maximum trust at minimum cost:**
```batch
1. build_menu.bat → Option 3 (Build MSIX)
2. Submit to Microsoft Store ($19)
3. Users install from Store (zero warnings!)
```
