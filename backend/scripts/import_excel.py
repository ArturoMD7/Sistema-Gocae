import os
import sys
import django
import pandas as pd
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from contratos.models import (
    Contrato, LineaTiempo, Ubicacion, Contratista, 
    PmtResumen, InversionEjercida, DatoGeologico
)

def clean_val(val):
    if pd.isna(val) or val == '(En blanco)' or val == 'N/A' or val == '':
        return None
    return val

def clean_float(val):
    c = clean_val(val)
    if c is not None:
        try:
            return float(c)
        except:
            return None
    return None

file_path = r'D:\PEMEX\Sistema-GOCAE\propuesta BD Grupal.xlsx'
xl = pd.ExcelFile(file_path)

# TABLA CONTRATO
df_contratos = xl.parse('TABLA CONTRATO')
for _, row in df_contratos.iterrows():
    cid = clean_val(row['ID_Contrato'])
    if not cid: continue
    
    # Check if exists
    Contrato.objects.update_or_create(
        contrato_id=cid,
        defaults={
            'modalidad': clean_val(row['Modalidad']),
            'ronda': clean_val(row['Ronda']),
            'licitacion': clean_val(row['Licitacion']),
            'area': clean_val(row['Area']),
            'pozos_comprometidos': clean_float(row['Pozos_Comprometidos']),
            'pozos_terminados': clean_float(row['Pozos_Terminados']),
            'operador_principal': clean_val(row['Operador_Principal']),
            'tipo_licitante': clean_val(row['Tipo_Licitante']),
            'tipo_yacimiento': clean_val(row['Tipo_Yacimiento']),
            'estado': clean_val(row['Estado']),
            'superficie_km2': clean_float(row['Superficie_km2']),
            'fecha_firma': clean_val(row.get('Fecha_Firma', None)),
            'duracion_anios': clean_float(row.get('Duracion_Años', None)),
            'vence': clean_val(row.get('Vence', None)),
            'estatus': clean_val(row['Estatus']),
            'participacion_estado': clean_float(row.get('Participacion_Estado', None))
        }
    )

# LINEA DEL TIEMPO
df_lt = xl.parse('LINEA DEL TIEMPO')
LineaTiempo.objects.all().delete()
for _, row in df_lt.iterrows():
    cid = clean_val(row['ID_Contrato'])
    if not cid: continue
    contrato = Contrato.objects.filter(contrato_id=cid).first()
    if contrato:
        LineaTiempo.objects.create(
            id_timeline=clean_val(row['ID_Timeline']) or str(_),
            contrato=contrato,
            fecha=str(clean_val(row['Fecha'])) if clean_val(row['Fecha']) else None,
            evento=clean_val(row['Evento']),
            detalles=clean_val(row['Detalles_Evento'])
        )

# UBICACION
df_ub = xl.parse('UBICACION')
Ubicacion.objects.all().delete()
for _, row in df_ub.iterrows():
    cid = clean_val(row['ID_Contrato'])
    if not cid: continue
    contrato = Contrato.objects.filter(contrato_id=cid).first()
    if contrato:
        Ubicacion.objects.create(
            id_punto=clean_val(row['ID_Punto']) or str(_),
            contrato=contrato,
            numero_vertice=clean_float(row['Numero_Vertice']),
            longitud=clean_float(row['Longitud_Decimales']),
            latitud=clean_float(row['Latitud_Decimales'])
        )

# CONTRATISTA
df_soc = xl.parse('CONTRATISTA')
Contratista.objects.all().delete()
for _, row in df_soc.iterrows():
    cid = clean_val(row['ID_Contrato'])
    if not cid: continue
    contrato = Contrato.objects.filter(contrato_id=cid).first()
    if contrato:
        Contratista.objects.create(
            id_socio=clean_val(row['ID_Socio']) or str(_),
            contrato=contrato,
            empresa_nombre=clean_val(row['Empresa_Nombre']),
            tipo_participacion=clean_val(row['Tipo_Participacion']),
            porcentaje_participacion=clean_float(row['Porcentaje_Participacion'])
        )

# PTM RESUMEN
df_pmt = xl.parse('PTM RESUMEN')
PmtResumen.objects.all().delete()
for _, row in df_pmt.iterrows():
    cid = clean_val(row['ID_Contrato'])
    if not cid: continue
    contrato = Contrato.objects.filter(contrato_id=cid).first()
    if contrato:
        PmtResumen.objects.create(
            id_pmt=clean_val(row['ID_PMT']) or str(_),
            contrato=contrato,
            programa_minimo=clean_float(row['Programa_Minimo_Trabajo_UT']),
            incremento=clean_float(row['Incremento_PMT_UT']),
            periodo_adicional=clean_float(row['Periodo_Adicional_UT']),
            total_requerido=clean_float(row['PMT_Total_Requerido']),
            acreditadas=clean_float(row['Acreditadas_Reales']),
            fecha_limite=str(clean_val(row['Fecha_Limite'])) if clean_val(row['Fecha_Limite']) else None
        )

# INVERSIONES EJERCIDAS
df_inv = xl.parse('INVERSIONES EJERCIDAS')
InversionEjercida.objects.all().delete()
for _, row in df_inv.iterrows():
    cid = clean_val(row['ID_Contrato'])
    if not cid: continue
    contrato = Contrato.objects.filter(contrato_id=cid).first()
    if contrato:
        InversionEjercida.objects.create(
            id_inversion=clean_val(row['ID_Inversion']) or str(_),
            contrato=contrato,
            anio=clean_float(row.get('Año', row.get('Ao', None))),
            mes=str(clean_val(row['Mes'])) if clean_val(row['Mes']) else None,
            monto_ejercido_usd=clean_float(row['Monto_Ejercido_USD'])
        )

# DATOS GEOLOGICOS
df_geo = xl.parse('DATOS GEOLOGICOS')
DatoGeologico.objects.all().delete()
for _, row in df_geo.iterrows():
    cid = clean_val(row['ID_Contrato'])
    if not cid: continue
    contrato = Contrato.objects.filter(contrato_id=cid).first()
    if contrato:
        DatoGeologico.objects.create(
            id_datgeo=clean_val(row['ID_DatGeo']) or str(_),
            contrato=contrato,
            provincia_petrolera=clean_val(row['Provincia_Petrolera']),
            provincia_geologica=clean_val(row['Provincia_Geologica']),
            superficie=clean_val(row['Superficie_AContractual_km2']),
            cobertura=clean_val(row['Cobertura_sismica_3D']),
            edad_play=clean_val(row['Edad_Play']),
            litologias=clean_val(row['Litologias']),
            hidrocarburo=clean_val(row['Hidrocarburo_Esperado'])
        )

print("Datos importados exitosamente desde Excel.")
