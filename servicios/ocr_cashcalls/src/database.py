import sqlite3
import os
from pathlib import Path

DB_PATH = Path("data/db/memory.db")

def get_connection():
    """Devuelve una conexión a la base de datos SQLite."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # Para poder acceder a las columnas por nombre
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos y crea las tablas si no existen."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla para correcciones de OCR de los usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ocr_corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT UNIQUE NOT NULL,
            corrected_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla para alias de campos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS field_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias_name TEXT UNIQUE NOT NULL,
            canonical_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_number TEXT UNIQUE NOT NULL,
            contract_name TEXT,
            operator_name TEXT NOT NULL,
            operator_alias TEXT,
            operator_participation REAL,
            partner_name TEXT NOT NULL,
            partner_alias TEXT,
            partner_participation REAL,
            active INTEGER DEFAULT 1,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO active_contracts (
            contract_number,
            contract_name,
            operator_name,
            operator_alias,
            operator_participation,
            partner_name,
            partner_alias,
            partner_participation,
            active,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'CNH-R02-L01-A2.TM/2017',
        'Area Contractual 2',
        'PEMEX Exploracion y Produccion',
        'PEP; PEMEX',
        70.0,
        'Wintershall Dea Mexico, S. de R.L. de C.V.',
        'WSD; Wintershall; Wintershell',
        30.0,
        1,
        'Contrato base para pruebas beta GOCAE.',
    ))
    
    conn.commit()
    conn.close()

# Inicializar al importar
init_db()
