@echo off
chcp 65001 >nul
title OUTRIDERS Türkçe Yama Kurulumu

echo ========================================================
echo             OUTRIDERS TÜRKÇE YAMA KURULUMU
echo ========================================================
echo.

:: Oyunun acik olup olmadigini kontrol et
:CHECK_RUNNING
tasklist /FI "IMAGENAME eq OUTRIDERS-Win64-Shipping.exe" 2>NUL | find /I /N "OUTRIDERS-Win64-Shipping.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [UYARI] OUTRIDERS su anda acik gorunuyor!
    echo Lutfen oyunu kapatin ve ardindan devam etmek icin bir tusa basin...
    pause >nul
    goto CHECK_RUNNING
)

:: Eski hatali ~mods paketlerini temizle (cokecegi icin)
if exist "Madness\Content\Paks\~mods\Outriders_Turkish_P.pak" (
    del /F /Q "Madness\Content\Paks\~mods\Outriders_Turkish_P.pak" >nul
)
if exist "Madness\Content\Paks\pakchunk00_s00-WindowsNoEditor_1_P.pak" (
    del /F /Q "Madness\Content\Paks\pakchunk00_s00-WindowsNoEditor_1_P.pak" >nul
)

echo [1/2] Turkce dil dosyasi yukleniyor...
if not exist "Madness\Content\Localization\Game\en" mkdir "Madness\Content\Localization\Game\en"

if exist "patch_files\Game.locres" (
    copy /Y "patch_files\Game.locres" "Madness\Content\Localization\Game\en\Game.locres" >nul
) else if exist "extracted_loc\Game_tr.locres" (
    copy /Y "extracted_loc\Game_tr.locres" "Madness\Content\Localization\Game\en\Game.locres" >nul
)

if not exist "Madness\Content\Localization\Game\en\Game.locres" (
    echo [HATA] Turkce Game.locres dosyasi bulunamadi!
    pause
    exit /b 1
)
echo [TAMAM] Turkce dil dosyasi basariyla yerlestirildi.

echo [2/2] Pak dil yonlendirmesi uygulaniyor...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$path = 'Madness\Content\Paks\pakchunk00_s00-WindowsNoEditor_0_P.pak'; " ^
    "if (-not (Test-Path $path)) { Write-Host '[HATA] Pak dosyasi bulunamadi! Kurulumu oyunun ana dizininde calistirdiginizdan emin olun.' -ForegroundColor Red; exit 1 }; " ^
    "$fs = [System.IO.File]::Open($path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite); " ^
    "$fs.Seek(2626660779, [System.IO.SeekOrigin]::Begin) | Out-Null; " ^
    "$fs.Write([byte[]]@(0x78, 0x78), 0, 2); " ^
    "$fs.Close(); " ^
    "Write-Host '[TAMAM] Pak yonlendirmesi basariyla uygulandi!' -ForegroundColor Green"

if "%ERRORLEVEL%"=="0" (
    echo.
    echo ========================================================
    echo   TÜRKÇE YAMA BAŞARIYLA KURULDU VE AKTİF EDİLDİ!
    echo   Oyunu Steam üzerinden başlatabilirsiniz. İyi oyunlar!
    echo ========================================================
) else (
    echo.
    echo [HATA] Pak dosyasina yazilamadi. Lutfen Yonetici olarak calistirin!
)

echo.
pause
