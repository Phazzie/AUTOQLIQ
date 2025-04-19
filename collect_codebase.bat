@echo off
echo Collecting codebase files for review...
cd /d %~dp0
python collect_codebase.py
echo Done! Check codebase_for_review.txt for the collected code.
pause
