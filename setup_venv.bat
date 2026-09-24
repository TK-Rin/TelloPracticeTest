@echo off
REM Recreates the virtual environment for THIS project, wherever it is
REM plugged in. A .venv folder cannot just be copied between PCs (it has
REM absolute paths baked in), so run this once on every new machine.
REM
REM %~dp0 = the folder this .bat file lives in, whatever drive letter that
REM turns out to be (G:, D:, E:, ...) on the PC you plugged the disk into.

cd /d "%~dp0"

py -3.11 -m venv .venv
if errorlevel 1 (
    echo.
    echo Could not find Python 3.11 via "py -3.11". Falling back to "python".
    python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Done. Next time, activate with:  .venv\Scripts\activate.bat
pause
