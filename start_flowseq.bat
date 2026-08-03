@echo off
:: ???? 5173 ?? node ??
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%a >nul 2>&1
set PATH=C:\Program Files\nodejs;%PATH%
cd /d E:\skills\bioinformatics-workflows
start /B npm run dev -- --host --port 5173
:wait
timeout /T 2 /NOBREAK >nul
netstat -ano | findstr ":5173.*LISTENING" >nul
if %errorlevel% neq 0 goto wait
start http://localhost:5173
