@echo off
title FlowSeq
cd /d "%~dp0"

if not exist node_modules\ (
    echo First run: installing dependencies...
    call npm install
    echo.
)

echo Starting FlowSeq (dev mode)...
call npm run dev -- --host --open
