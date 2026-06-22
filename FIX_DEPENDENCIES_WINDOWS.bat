@echo off
cd /d "%~dp0"
echo ============================================
echo Fixing Python package dependency issue
echo ============================================
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
python -m pip uninstall -y rdflib pyparsing
python -m pip install --no-cache-dir -r requirements.txt
python -m pip show rdflib pyparsing
echo.
echo Running functionality tests...
python run_tests.py
echo.
echo Starting Flask website...
python app.py
pause
