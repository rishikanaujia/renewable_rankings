@echo off
REM Memory & Learning System - Windows Installation Script

echo ========================================
echo Memory ^& Learning System - Installer
echo ========================================
echo.

REM Check if package exists
if not exist "memory_system_complete.tar.gz" (
    echo Error: memory_system_complete.tar.gz not found!
    echo Please download the package first.
    pause
    exit /b 1
)

REM Get project root (default: current directory)
set "PROJECT_ROOT=%~1"
if "%PROJECT_ROOT%"=="" set "PROJECT_ROOT=."

echo Installation directory: %PROJECT_ROOT%
echo.
set /p CONFIRM="Install memory system to %PROJECT_ROOT%? (y/n) "
if /i not "%CONFIRM%"=="y" (
    echo Installation cancelled.
    pause
    exit /b 0
)

echo Extracting package...
tar -xzf memory_system_complete.tar.gz

echo Checking project structure...
if not exist "%PROJECT_ROOT%\src" mkdir "%PROJECT_ROOT%\src"
if not exist "%PROJECT_ROOT%\config" mkdir "%PROJECT_ROOT%\config"
if not exist "%PROJECT_ROOT%\docs" mkdir "%PROJECT_ROOT%\docs"
if not exist "%PROJECT_ROOT%\scripts" mkdir "%PROJECT_ROOT%\scripts"
if not exist "%PROJECT_ROOT%\data\memory" mkdir "%PROJECT_ROOT%\data\memory"

echo Installing files...
echo   - Copying memory module to src/
xcopy /E /I /Y memory_system\src\memory "%PROJECT_ROOT%\src\memory" > nul

echo   - Copying configuration
copy /Y memory_system\config\memory.yaml "%PROJECT_ROOT%\config\" > nul

echo   - Copying documentation
copy /Y memory_system\docs\MEMORY_SYSTEM_GUIDE.md "%PROJECT_ROOT%\docs\" > nul

echo   - Copying demo script
copy /Y memory_system\scripts\demo_memory_system.py "%PROJECT_ROOT%\scripts\" > nul

echo   - Copying reference documentation
copy /Y memory_system\MEMORY_INSTALLATION.md "%PROJECT_ROOT%\" > nul
copy /Y memory_system\MEMORY_QUICK_REFERENCE.md "%PROJECT_ROOT%\" > nul
copy /Y memory_system\MEMORY_SYSTEM_DELIVERY.md "%PROJECT_ROOT%\" > nul

echo   - Updating requirements.txt
if exist "%PROJECT_ROOT%\requirements.txt" (
    findstr /C:"chromadb" "%PROJECT_ROOT%\requirements.txt" > nul
    if errorlevel 1 (
        echo. >> "%PROJECT_ROOT%\requirements.txt"
        echo # Memory ^& Learning System >> "%PROJECT_ROOT%\requirements.txt"
        echo chromadb^>=0.4.0 >> "%PROJECT_ROOT%\requirements.txt"
        echo sentence-transformers^>=2.2.0 >> "%PROJECT_ROOT%\requirements.txt"
    ) else (
        echo     (chromadb already in requirements.txt)
    )
) else (
    copy /Y memory_system\requirements.txt "%PROJECT_ROOT%\" > nul
)

REM Cleanup
rmdir /S /Q memory_system

echo.
echo ✓ Installation complete!
echo.
echo Files installed:
echo   • src\memory\ (14 Python modules)
echo   • config\memory.yaml
echo   • docs\MEMORY_SYSTEM_GUIDE.md
echo   • scripts\demo_memory_system.py
echo   • MEMORY_INSTALLATION.md
echo   • MEMORY_QUICK_REFERENCE.md
echo   • MEMORY_SYSTEM_DELIVERY.md
echo   • requirements.txt (updated)
echo.
echo Next steps:
echo   1. Install dependencies:
echo      pip install chromadb sentence-transformers
echo.
echo   2. Run demo to verify installation:
echo      cd %PROJECT_ROOT% ^&^& python scripts\demo_memory_system.py
echo.
echo   3. Read the documentation:
echo      type %PROJECT_ROOT%\MEMORY_INSTALLATION.md
echo.
echo   4. Start integrating with your agents:
echo      type %PROJECT_ROOT%\MEMORY_QUICK_REFERENCE.md
echo.
echo For detailed instructions, see: MEMORY_INSTALLATION.md
echo.
pause
