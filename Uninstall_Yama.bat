@echo off
chcp 65001 >nul
title OUTRIDERS Türkçe Yama Kaldırıcı

echo ========================================================
echo             OUTRIDERS TÜRKÇE YAMA KALDIRICI
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

echo [1/2] Pak dil ayari orijinal haline donduruluyor...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$path = 'Madness\Content\Paks\pakchunk00_s00-WindowsNoEditor_0_P.pak'; " ^
    "if (-not (Test-Path $path)) { Write-Host '[HATA] Pak dosyasi bulunamadi!' -ForegroundColor Red; exit 1 }; " ^
    "$fs = [System.IO.File]::Open($path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite); " ^
    "$fs.Seek(2626660779, [System.IO.SeekOrigin]::Begin) | Out-Null; " ^
    "$fs.Write([byte[]]@(0x65, 0x6E), 0, 2); " ^
    "$fs.Close(); " ^
    "Write-Host '[TAMAM] Pak dosyasi orijinal (en) haline donduruldu.' -ForegroundColor Green"

echo [2/2] Ek dil dosyalari temizleniyor...
if exist "Madness\Content\Localization\Game\en\Game.locres" (
    del /F /Q "Madness\Content\Localization\Game\en\Game.locres" >nul
)

echo.
echo ========================================================
echo   TÜRKÇE YAMA BAŞARIYLA KALDIRILDI!
echo   Oyun orijinal haline geri donduruldu.
echo ========================================================
echo.
pause
