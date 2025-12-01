#!/bin/bash
# ====================================================================
# Vibe-Code Auditor Build Script
# Automated executable build with PyInstaller (Linux/Mac)
# ====================================================================

echo "============================================================"
echo "  Vibe-Code Auditor v1.9.0 - Build Script"
echo "  Creating standalone executable"
echo "============================================================"
echo ""

# Check if PyInstaller is installed
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[ERROR] PyInstaller is not installed!"
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "[FAILED] Could not install PyInstaller"
        exit 1
    fi
fi

echo "[1/5] Checking dependencies..."
python3 -c "import streamlit, plotly, anthropic, rich" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[WARNING] Some dependencies are missing"
    echo "Installing requirements..."
    pip3 install -r requirements.txt
fi

echo "[2/5] Cleaning previous build..."
rm -rf build dist
echo "  - Removed build/ and dist/ directories"

echo "[3/5] Running PyInstaller..."
echo "  This may take 5-15 minutes..."
echo ""
pyinstaller VibeAuditor.spec
if [ $? -ne 0 ]; then
    echo ""
    echo "[FAILED] PyInstaller build failed!"
    echo "Check the error messages above."
    exit 1
fi

echo ""
echo "[4/5] Verifying build output..."
if [ -f "dist/VibeAuditor" ]; then
    echo "  ✓ VibeAuditor created successfully"
    ls -lh dist/VibeAuditor | awk '{print "  - Size: " $5}'
else
    echo "  ✗ Build failed - executable not found"
    exit 1
fi

echo "[5/5] Cleaning up temporary files..."
rm -rf build
echo "  - Removed build/ directory"

echo ""
echo "============================================================"
echo "  BUILD SUCCESSFUL!"
echo "============================================================"
echo ""
echo "Executable location: dist/VibeAuditor"
echo ""
echo "To run the executable:"
echo "  1. Make it executable: chmod +x dist/VibeAuditor"
echo "  2. Run: ./dist/VibeAuditor"
echo ""
echo "To distribute:"
echo "  - Copy the entire dist/ folder"
echo "  - Or create a tarball: tar -czf VibeAuditor.tar.gz dist/"
echo ""
echo "============================================================"
