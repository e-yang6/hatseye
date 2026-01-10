@echo off
REM Activate the virtual environment for Hat's Eye
call venv\Scripts\activate.bat
echo Virtual environment activated!
echo Python version:
python --version
echo.
echo All dependencies are installed. You can now run:
echo   python webcam_gemini.py
echo.
