@echo off
chcp 65001 >nul
cd /d "%~dp0game"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 chekushka_adventure.py
) else (
  python chekushka_adventure.py
)
if errorlevel 1 (
  echo.
  echo Не удалось запустить игру. Проверь, что установлен Python с Tcl/Tk.
  pause
)
