@echo off
REM ====================================================================
REM Vibe-Code Auditor Build Script
REM Automated executable build with PyInstaller
REM ====================================================================

echo ============================================================
echo   Vibe-Code Auditor v1.9.0 - Build Script
echo   Creating standalone Windows executable
echo ============================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller is not installed!
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [FAILED] Could not install PyInstaller
        pause
        exit /b 1
    )
)

echo [1/5] Checking dependencies...
python -c "import streamlit, plotly, anthropic, rich" 2>nul
if errorlevel 1 (
    echo [WARNING] Some dependencies are missing
    echo Installing requirements...
    pip install -r requirements.txt
)

echo [2/5] Cleaning previous build...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo   - Removed build/ and dist/ directories

echo [3/5] Running PyInstaller...
echo   This may take 5-15 minutes...
echo.
pyinstaller VibeAuditor.spec
if errorlevel 1 (
    echo.
    echo [FAILED] PyInstaller build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo [4/5] Verifying build output...
if exist "dist\VibeAuditor.exe" (
    echo   ✓ VibeAuditor.exe created successfully
    for %%I in ("dist\VibeAuditor.exe") do echo   - Size: %%~zI bytes
) else (
    echo   ✗ Build failed - executable not found
    pause
    exit /b 1
)

echo [5/5] Cleaning up temporary files...
rmdir /s /q "build" 2>nul
echo   - Removed build/ directory

echo.
echo ============================================================
echo   BUILD SUCCESSFUL!
echo ============================================================
echo.
echo Executable location: dist\VibeAuditor.exe
echo.
echo To run the executable:
echo   1. Navigate to: dist\
echo   2. Double-click: VibeAuditor.exe
echo   3. Or run from command line: dist\VibeAuditor.exe
echo.
echo To distribute:
echo   - Copy the entire dist\ folder
echo   - Or zip dist\VibeAuditor.exe with dependencies
echo.
echo ============================================================
pause
