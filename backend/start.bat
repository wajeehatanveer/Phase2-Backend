@echo off
setlocal

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    pip install -r requirements.txt
)

REM Start the FastAPI application using uvicorn
python3 -m uvicorn main:app --host 0.0.0.0 --port %PORT%