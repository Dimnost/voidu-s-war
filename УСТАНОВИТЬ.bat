@echo off
chcp 65001 >nul
title Установка Chekushka Adventure
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer.ps1"
if errorlevel 1 (
  echo.
  echo Установка завершилась с ошибкой. Скопируй текст ошибки и отправь его мне.
  pause
)
