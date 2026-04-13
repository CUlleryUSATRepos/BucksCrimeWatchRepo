@echo off

cd /d "C:\Users\Chris Ullery\PycharmProjects\NewCrimewatch"

call .venv\Scripts\activate

echo Running FULL pipeline...

python scripts\fetch_directory_links.py || exit /b
python scripts\run_all_agencies.py || exit /b
python scripts\filter_today_posts.py || exit /b
python scripts\build_today_json.py || exit /b

echo Done.
pause