@echo off
echo ===================================================
echo   INICIANDO SERVICIOS DEL SISTEMA GOCAE
echo ===================================================
echo.

echo Iniciando Backend (Django) en el puerto 8000...
start cmd /k "cd backend && call venv-gocae\Scripts\activate && python manage.py runserver"

echo Iniciando Microservicio OCR (FastAPI) en el puerto 8001...
start cmd /k "cd servicios\ocr_cashcalls && call venv-ocr\Scripts\activate && uvicorn main:app --port 8001 --reload"

echo Iniciando Frontend (Vue) en el puerto 5173...
start cmd /k "cd frontend && npm run dev"

echo.
echo Todos los servicios han sido lanzados en ventanas separadas.
echo Cierra las ventanas individuales para detener los servicios.
pause
