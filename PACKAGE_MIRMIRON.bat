@echo off
chcp 65001 >nul
title MIR MIRON - PACKAGE (materiallar tuzatildi)
echo ================================================================
echo   MIR MIRON - QAYTA PACKAGE
echo   Materiallar tuzatildi (43 material - MMFix), Nanite EXE-soya
echo ================================================================
echo.
echo MUHIM: Unreal Editor TO'LIQ YOPIQ bulishi shart!
echo   (MCP port 8000 band bulsa cook xato beradi - ExitCode 25)
echo.
echo Tayyor bulsa ENTER bosing (yoki oynani yoping bekor qilish uchun).
pause >nul
echo.
echo [%TIME%] Package boshlandi. Bu ~1-2 soat oladi (28GB).
echo Bu oynani YOPMANG - jarayon shu yerda ketadi.
echo ----------------------------------------------------------------
echo.

del "E:\MIR MIRON PACKAGE\_PACKAGE_DONE.txt" 2>nul

call "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun -project="D:\O\Odilbek.uproject" -noP4 -platform=Win64 -clientconfig=Development -build -cook -stage -pak -archive -prereqs -archivedirectory="E:\MIR MIRON PACKAGE" -utf8output -nocompileeditor

echo.
echo ----------------------------------------------------------------
if %ERRORLEVEL% EQU 0 (
  echo   TUGADI - MUVAFFAQIYATLI [BUILD SUCCESSFUL]
  echo   EXE: E:\MIR MIRON PACKAGE\Windows\Odilbek.exe
  echo TUGADI %DATE% %TIME% > "E:\MIR MIRON PACKAGE\_PACKAGE_DONE.txt"
) else (
  echo   XATO - ExitCode %ERRORLEVEL%
  echo   Agar 25 bulsa: Editor hali ochiq edi. Yoping va qayta bosing.
  echo XATO ExitCode %ERRORLEVEL% %DATE% %TIME% > "E:\MIR MIRON PACKAGE\_PACKAGE_DONE.txt"
)
echo ----------------------------------------------------------------
echo.
echo Yopish uchun ENTER bosing.
pause >nul
