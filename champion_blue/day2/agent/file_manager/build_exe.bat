@echo off
chcp 65001 >nul
echo ========================================
echo  파일 관리자 EXE 빌드 스크립트
echo ========================================
echo.

:: PyInstaller 설치 확인
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [설치] PyInstaller 설치 중...
    pip install pyinstaller
)

echo.
echo [빌드] EXE 파일 생성 중... (1~3분 소요)
echo.

:: 빌드 명령 (단일 EXE, 콘솔창 없음, 아이콘 옵션 포함)
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "파일관리자" ^
  --add-data "." ^
  file_manager.py

:: 빌드 결과 이동
if exist dist\파일관리자.exe (
    echo.
    echo ========================================
    echo  빌드 완료!
    echo  결과 파일: dist\파일관리자.exe
    echo ========================================
    explorer dist
) else (
    echo.
    echo [오류] 빌드에 실패했습니다. 위 로그를 확인하세요.
)

pause
