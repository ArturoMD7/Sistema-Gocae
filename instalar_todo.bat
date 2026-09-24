@echo off
echo ===================================================
echo   INSTALADOR AUTOMATICO DE ENTRONOS - SISTEMA GOCAE
echo ===================================================
echo.

echo [1/3] Instalando dependencias del Backend (Django)...
cd backend
python -m venv venv-gocae
call venv-gocae\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..
echo Backend listo!
echo.

echo [2/3] Instalando dependencias de Microservicios (OCR)...
cd servicios\ocr_cashcalls
python -m venv venv-ocr
call venv-ocr\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..\..
echo OCR listo!
echo.

echo [3/3] Instalando dependencias del Frontend (Vue)...
cd frontend
call npm install
cd ..
echo Frontend listo!
echo.

echo ===================================================
echo   INSTALACION COMPLETADA EXITOSAMENTE!
echo   Ya puedes ejecutar "iniciar_todo.bat"
echo ===================================================
pause
