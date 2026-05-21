@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
cd /d "%~dp0"

title FiscalBot - Iniciando

echo.
echo  ========================================
echo   FiscalBot - Inicializacao automatica
echo  ========================================
echo.

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Docker nao encontrado. Instale o Docker Desktop e tente novamente.
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Docker Desktop nao esta em execucao. Abra o Docker Desktop e tente novamente.
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo [OK] Arquivo .env criado a partir de .env.example
    ) else (
        echo [AVISO] .env.example nao encontrado; usando padroes do Docker Compose.
    )
)

if not exist "fiscalbot-web\.env" (
    if exist "fiscalbot-web\.env.example" (
        copy /Y "fiscalbot-web\.env.example" "fiscalbot-web\.env" >nul
        echo [OK] fiscalbot-web\.env criado
    )
)

echo.
echo [1/5] Subindo containers (Postgres, Redis, API, Worker, Beat)...
docker compose up --build -d
if errorlevel 1 (
    echo [ERRO] Falha ao iniciar containers.
    pause
    exit /b 1
)

echo.
echo [2/5] Aguardando API ficar pronta...
set /a TENTATIVAS=0
:aguardar_api
set /a TENTATIVAS+=1
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 3).StatusCode | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 goto api_pronta
if %TENTATIVAS% GEQ 45 (
    echo [ERRO] API nao respondeu em tempo habil. Execute: docker compose logs api
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto aguardar_api
:api_pronta
echo [OK] API respondendo em http://localhost:8000

echo.
echo [3/5] Aplicando migracoes do banco...
docker compose exec -T api alembic upgrade head
if errorlevel 1 (
    echo [AVISO] Migracao falhou; verifique os logs da API.
)

echo.
echo [4/5] Carregando dados de demonstracao (seed)...
docker compose exec -T api python scripts/seed.py
if errorlevel 1 (
    echo [AVISO] Seed falhou; dados podem ja existir.
)

echo.
echo [5/5] Iniciando frontend React...
if not exist "fiscalbot-web\node_modules" (
    echo       Instalando dependencias npm (primeira vez)...
    pushd fiscalbot-web
    call npm install
    if errorlevel 1 (
        popd
        echo [ERRO] npm install falhou no frontend.
        pause
        exit /b 1
    )
    popd
)

start "FiscalBot - Frontend" cmd /k "cd /d "%~dp0fiscalbot-web" && title FiscalBot Frontend && npm run dev"

echo       Aguardando frontend...
timeout /t 6 /nobreak >nul

start "" "http://localhost:5173"
start "" "http://localhost:8000/docs"

echo.
echo  ========================================
echo   FiscalBot em execucao!
echo  ========================================
echo.
echo   Frontend:  http://localhost:5173
echo   API Docs:  http://localhost:8000/docs
echo   Health:    http://localhost:8000/health
echo.
echo   Login demo:
echo     E-mail: admin@fiscalbot.gov.br
echo     Senha:  fiscalbot123
echo.
echo   Para encerrar tudo, execute: parar-fiscalbot.bat
echo.
pause
endlocal
