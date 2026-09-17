@echo off
echo Setting up Flashcards for Developers...

echo Creating data and src directories...
if not exist data mkdir data
if not exist src mkdir src

echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment and installing requirements...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo Initialization complete! 
echo To run the app:
echo 1. call venv\Scripts\activate.bat
echo 2. streamlit run src\app.py
pause
