@echo off
echo Starting HR AI Agent Backend...
echo.
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
pause







