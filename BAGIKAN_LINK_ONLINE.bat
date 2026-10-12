@echo off
title BPH Website - Link Online Publik
echo ============================================================
echo   MEMBUAT LINK ONLINE DEMO BPH (CLOUDFLARE TUNNEL)
echo ============================================================
echo.
echo Pastikan server Django lokal Anda sedang berjalan (port 8000).
echo.
echo Salin link https://xxxx.trycloudflare.com yang muncul di bawah ini
echo untuk dibagikan ke orang lain / dibuka di HP.
echo.
echo Tekan Ctrl + C untuk mematikan link online jika sudah selesai.
echo ============================================================
echo.
.\cloudflared.exe tunnel --url http://127.0.0.1:8000
pause
