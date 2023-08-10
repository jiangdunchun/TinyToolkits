@echo off
cd %1

:loop
git pull
if %errorlevel% equ 0 (
  echo Git pull successful.
  goto end
) else (
  echo Git pull failed. retrying...
  timeout /t 5 >nul
  goto loop
)

:end
