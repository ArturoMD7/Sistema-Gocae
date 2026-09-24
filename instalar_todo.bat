@echo off
echo ===================================================
echo   INSTALADOR AUTOMATICO DE ENTORNOS - SISTEMA GOCAE
echo ===================================================
echo.

echo [1/3] Instalando dependencias del Backend (Django)...
cd backend
python -m venv venv-gocae
call venv-gocae\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
call deactivate
cd ..
echo Backend listo!
pause
echo.

echo [2/3] Instalando dependencias de Microservicios (OCR)...
cd servicios\ocr_cashcalls
python -m venv venv-ocr
call venv-ocr\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
call deactivate
cd ..\..
echo OCR listo!
pause
echo.

echo [3/3] Instalando dependencias del Frontend (Vue)...
cd frontend
call pnpm install
cd ..
echo Frontend listo!
echo.

echo ===================================================
echo   INSTALACION COMPLETADA EXITOSAMENTE!
echo   Ya puedes ejecutar "iniciar_todo.bat"
echo ===================================================
pause
