@echo off
title Flashcards for Developers
echo ============================================
echo         Flashcards for Developers
echo ============================================
echo.
echo Iniciando o aplicativo...
echo O navegador abrira automaticamente.
echo Para encerrar o app, feche esta janela.
echo.

REM Caminho absoluto baseado na localização do .bat
set BASEDIR=%~dp0

call "%BASEDIR%venv\Scripts\activate.bat"

python -m streamlit run "%BASEDIR%src\app.py"  --server.headless false

pause
