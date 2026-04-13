@echo off
cd /d "C:\Users\Chris Ullery\PycharmProjects\NewCrimewatch"

call .venv\Scripts\activate.bat

cd scripts
python scrape_press_releases.py
cd ..

git add scripts\data\today_posts.csv
git commit -m "Auto update CrimeWatch dashboard"
git push