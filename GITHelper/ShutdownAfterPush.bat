@echo off
cd %1

:loop
git push
if %errorlevel% equ 0 (
  echo git push successful.
  goto end
) else (
  echo git push failed. retrying...
  timeout /t 5 >nul
  goto loop
)

:end
echo shutdown after 60s. Press ctrl+c to interrupt
timeout /t 60 >nul
shutdown -s -t 0
