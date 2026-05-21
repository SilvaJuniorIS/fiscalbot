@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
cd /d "%~dp0"

title FiscalBot - Encerrando

echo.
echo  ========================================
echo   FiscalBot - Encerrando servicos
echo  ========================================
echo.

where docker >nul 2>&1
if not errorlevel 1 (
    echo [1/2] Parando containers Docker...
    docker compose down
    if errorlevel 1 (
        echo [AVISO] Nao foi possivel derrubar todos os containers.
    ) else (
        echo [OK] Containers encerrados.
    )
) else (
    echo [AVISO] Docker nao encontrado; pulando compose down.
)

echo.
echo [2/2] Encerrando janela do frontend (se aberta)...
taskkill /FI "WINDOWTITLE eq FiscalBot - Frontend*" /T /F >nul 2>&1

echo.
echo  FiscalBot encerrado.
echo.
pause
endlocal
