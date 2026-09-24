from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI(title="OCR CashCalls API", version="1.0")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "OCR Service is running"}

@app.post("/api/extract/cashcall")
async def extract_cashcall(file: UploadFile = File(...)):
    # Aquí integraremos la lógica de src/extractor.py
    # Por ahora devolvemos un mock para probar la conexión
    file_bytes = await file.read()
    return {
        "filename": file.filename,
        "size": len(file_bytes),
        "status": "procesado",
        "data": {
            "Total Current Period": 1000.50,
            # más campos mock...
        }
    }
