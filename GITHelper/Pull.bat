@echo off
cd %1

:loop
git pull
if %errorlevel% equ 0 (
  echo git pull successful.
  goto end
) else (
  echo git pull failed. retrying...
  timeout /t 5 >nul
  goto loop
)

:end
