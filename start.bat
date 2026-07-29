@echo off
title FlowSeq
cd /d "E:\skills\bioinformatics-workflows"

if not exist dist\ (
    echo First run: building...
    call npm install
    call npm run build
    echo.
)

echo Starting FlowSeq...
start http://localhost:5173/bioinformatics-workflows/
call npx vite preview --port 5173
