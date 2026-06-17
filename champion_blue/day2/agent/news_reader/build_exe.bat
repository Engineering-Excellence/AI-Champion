@echo off
chcp 65001 >nul
echo ============================================
echo   정책브리핑 뉴스 리더  EXE 빌드
echo ============================================
echo.

pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [설치] PyInstaller 설치 중...
    pip install pyinstaller
)

echo [빌드] EXE 생성 중... (1~3분 소요)
echo.

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "정책뉴스리더" ^
  news_gui.py

if exist dist\정책뉴스리더.exe (
    echo.
    echo ============================================
    echo   완료! dist\정책뉴스리더.exe
    echo ============================================
    explorer dist
) else (
    echo [오류] 빌드 실패. 위 로그를 확인하세요.
)
pause
