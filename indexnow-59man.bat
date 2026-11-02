@echo off
setlocal EnableExtensions
chcp 65001 >nul
title 59man.shop IndexNow
echo.
echo ======================================
echo   59man.shop - IndexNow (NAVER)
echo ======================================
echo 1 - Submit all sitemap URLs (initial/full)
echo 2 - Submit one new or updated URL
echo 3 - Check key and show URLs (dry run)
echo.
set /p "MODE=Select 1, 2 or 3: "
if "%MODE%"=="1" (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0indexnow-59man.ps1" -Mode sitemap
) else if "%MODE%"=="2" (
  set /p "TARGET=Full page URL: "
  call :single
) else if "%MODE%"=="3" (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0indexnow-59man.ps1" -Mode sitemap -DryRun
) else (
  echo Invalid selection. No URLs submitted.
)
echo.
pause
exit /b
:single
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0indexnow-59man.ps1" -Mode single -Url "%TARGET%"
exit /b
