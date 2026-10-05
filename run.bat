@echo off
chcp 65001 >nul
setlocal

title CleanAPIs Auto
cd /d "%~dp0"

rem ---- cari python (python atau py) ----
set "PYCMD="
where python >nul 2>&1 && set "PYCMD=python"
if not defined PYCMD where py >nul 2>&1 && set "PYCMD=py"
if not defined PYCMD (
    echo  [ERROR] python tidak ditemukan di PATH.
    echo  instal python 3.10+ dari https://python.org, centang "Add to PATH".
    echo  kalau sudah instal coba ketik "py" di cmd.
    echo.
    pause
    exit /b 1
)

rem ---- versi python harus 3.10+ ----
%PYCMD% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 goto :errver
for /f "tokens=*" %%v in ('%PYCMD% --version 2^>^&1') do set "VER=%%v"

rem ---- cek apakah setup diperlukan ----
set "NEED_SETUP=0"
%PYCMD% -c "import camoufox, playwright" >nul 2>&1
if errorlevel 1 set "NEED_SETUP=1"
%PYCMD% -m camoufox path >nul 2>&1
if errorlevel 1 set "NEED_SETUP=1"

if "%NEED_SETUP%"=="0" goto :langsung

rem ---- SETUP: deps / browser belum ada -> tampilkan progress instal ----
echo  [1/4] python ditemukan: %VER% (%PYCMD%)
echo.

rem ---- install dependencies ----
%PYCMD% -c "import camoufox, playwright" >nul 2>&1
if errorlevel 1 (
    echo  [2/4] memasang dependencies ...
    echo.
    %PYCMD% -m pip install --upgrade pip
    %PYCMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo  [ERROR] gagal memasang dependencies.
        echo  coba: %PYCMD% -m pip install camoufox[geoip]^>=0.5.6 playwright^>=1.62.0
        echo.
        pause
        exit /b 1
    )
) else (
    echo  [2/4] dependencies sudah terpasang - skip
)

rem ---- download browser Camoufox ----
%PYCMD% -m camoufox path >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [3/4] mengunduh browser Camoufox ...
    echo.
    %PYCMD% -m camoufox fetch
    if errorlevel 1 (
        echo.
        echo  [ERROR] gagal mengunduh browser Camoufox.
        echo  coba: %PYCMD% -m camoufox fetch
        echo.
        pause
        exit /b 1
    )
) else (
    echo  [3/4] browser Camoufox sudah ada - skip
)

echo.
echo  [4/4] menjalankan CleanAPIs Auto ...
echo.
%PYCMD% main.py
if errorlevel 1 (
    echo.
    echo  [ERROR] ada error, cek pesan di atas.
    echo.
    pause
    exit /b 1
)
echo.
echo  selesai. tekan tombol apapun untuk keluar.
pause
exit /b 0

:langsung
rem ---- SUDAH SIAP: langsung masuk sistem utama tanpa log installer ----
%PYCMD% main.py
if errorlevel 1 (
    echo.
    echo  [ERROR] ada error, cek pesan di atas.
    echo.
    pause
    exit /b 1
)
echo.
echo  selesai. tekan tombol apapun untuk keluar.
pause
exit /b 0

:errver
echo  [ERROR] python %VER% terlalu tua - butuh 3.10+.
echo  update di https://python.org
echo.
pause
exit /b 1
