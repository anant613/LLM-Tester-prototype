@echo off
echo Starting Backend Server...
start cmd /k "cd backend && C:\Users\anant\AppData\Local\Programs\Python\Python314\python.exe -m uvicorn main:app --reload"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
