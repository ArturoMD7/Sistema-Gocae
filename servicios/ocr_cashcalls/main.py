from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from src.invoice_extractor import extract_invoice_data

app = FastAPI(title="OCR CashCalls API", version="1.0")

# Permitir peticiones desde Vue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "OCR Service is running"}

@app.post("/api/extract/invoice")
async def extract_invoice(
    file: UploadFile = File(...),
    pct_operador: float = Form(70.0),
    pct_socio: float = Form(30.0)
):
    content = await file.read()
    xml_str = content.decode('utf-8', errors='ignore')
    
    # Procesar el XML
    data = extract_invoice_data(
        xml_content=xml_str,
        file_name=file.filename,
        file_path=file.filename,
        pct_operador=pct_operador,
        pct_socio=pct_socio
    )
    
    return {
        "status": "success",
        "filename": file.filename,
        "data": data
    }

from pydantic import BaseModel
from fastapi.responses import Response
from src.excel_exporter import excel_to_bytes
import pandas as pd

class ExportRequest(BaseModel):
    data: List[dict]

@app.post("/api/export/excel")
async def export_excel(req: ExportRequest):
    if not req.data:
        return {"status": "error", "message": "No data to export"}
    df = pd.DataFrame(req.data)
    excel_bytes = excel_to_bytes(df)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Facturas.xlsx"}
    )
