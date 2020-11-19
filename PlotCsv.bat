@echo off
setlocal
echo "Starting PlotCsv . . ."

call activate aps
python main.py
pause
call deactivate
