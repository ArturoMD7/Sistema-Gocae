import xml.etree.ElementTree as ET
from datetime import datetime
import math
import re

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def format_amount(amount_str: str) -> str:
    try:
        return f"{float(amount_str):.2f}"
    except (ValueError, TypeError):
        return amount_str or "0.00"

def extract_invoice_data(xml_content: str, file_name: str, file_path: str, pct_operador: float = 70.0, pct_socio: float = 30.0) -> list[dict]:
    error_row = {
        "Folio Fiscal": "", "Serie y folio": "", "Fecha": "", "Año": "", "Trimestre": "", "Mes": "", "Nombre Mes": "",
        "Emisor Rfc": "", "Nombre Emisor": "", "Receptor Rfc": "", "Nombre Receptor": "",
        "Tipo de Comprobante": "", "Estado": "Error", "Moneda": "", "Forma de pago": "", "Metodo de pago": "", "Condiciones de Pago": "",
        "SubTotal": "0.00", "Iva Trasladado": "0.00", "Iva Retenido": "0.00", "Total": "0.00",
        "Monto Operador": "0.00", "Monto Socio": "0.00",
        "Num Concepto": "", "Clave": "", "Cantidad": "", "Tarea": "", "Descripcion": "", "Importe": "0.00",
        "Archivo": file_name, "Ruta": file_path, "Alertas": ""
    }
    
    try:
        if xml_content.startswith("<?xml"):
            xml_content = xml_content.split("?>", 1)[-1].strip()
        root = ET.fromstring(xml_content)
    except Exception as e:
        error_row["Alertas"] = f"Error parseando XML: {str(e)}"
        return [error_row]
        
    def find_node(node, target_name):
        if node.tag.split('}')[-1] == target_name:
            return node
        for child in node:
            res = find_node(child, target_name)
            if res is not None:
                return res
        return None
        
    def find_all_nodes(node, target_name, results=None):
        if results is None:
            results = []
        if node.tag.split('}')[-1] == target_name:
            results.append(node)
        for child in node:
            find_all_nodes(child, target_name, results)
        return results

    comprobante = find_node(root, "Comprobante") or root
    
    tfd = find_node(root, "TimbreFiscalDigital")
    folio_fiscal = tfd.get("UUID", "") if tfd is not None else ""
    
    serie = comprobante.get("Serie", "")
    folio = comprobante.get("Folio", "")
    serie_folio = f"{serie} {folio}".strip()
    
    raw_fecha = comprobante.get("Fecha", "")
    fecha = ""
    anio = ""
    mes = ""
    nombre_mes = ""
    trimestre = ""
    
    if raw_fecha:
        try:
            dt = datetime.fromisoformat(raw_fecha)
            fecha = dt.strftime("%d/%m/%Y")
            anio = str(dt.year)
            mes = f"{dt.month}"
            nombre_mes = MESES.get(dt.month, "")
            trimestre = f"T{math.ceil(dt.month / 3)}"
        except ValueError:
            fecha = raw_fecha
            
    emisor = find_node(root, "Emisor")
    emisor_rfc = emisor.get("Rfc", "") if emisor is not None else ""
    nombre_emisor = emisor.get("Nombre", "") if emisor is not None else ""
    
    receptor = find_node(root, "Receptor")
    receptor_rfc = receptor.get("Rfc", "") if receptor is not None else ""
    nombre_receptor = receptor.get("Nombre", "") if receptor is not None else ""
    
    tipo = comprobante.get("TipoDeComprobante", "")
    if tipo.upper() == "I":
        tipo_comprobante = "I ingreso"
    elif tipo.upper() == "E":
        tipo_comprobante = "E egreso"
    else:
        tipo_comprobante = tipo
        
    moneda = comprobante.get("Moneda", "")
    forma_pago = comprobante.get("FormaPago", "")
    metodo_pago = comprobante.get("MetodoPago", "")
    condiciones_pago = comprobante.get("CondicionesDePago", "")
    
    subtotal = comprobante.get("SubTotal", "0")
    total = comprobante.get("Total", "0")
    
    try:
        total_val = float(total)
        monto_operador = f"{total_val * (pct_operador / 100.0):.2f}"
        monto_socio = f"{total_val * (pct_socio / 100.0):.2f}"
    except ValueError:
        monto_operador = "0.00"
        monto_socio = "0.00"

    impuestos_global = None
    for child in root:
        if child.tag.split('}')[-1] == "Impuestos":
            impuestos_global = child
            break
            
    iva_trasladado = "0.00"
    iva_retenido = "0.00"
    if impuestos_global is not None:
        iva_trasladado = impuestos_global.get("TotalImpuestosTrasladados", "0.00")
        iva_retenido = impuestos_global.get("TotalImpuestosRetenidos", "0.00")

    # Formateamos valores monetarios globales
    subtotal_f = format_amount(subtotal)
    iva_trasladado_f = format_amount(iva_trasladado)
    iva_retenido_f = format_amount(iva_retenido)
    total_f = format_amount(total)

    conceptos_node = find_node(root, "Conceptos")
    conceptos_list = []
    
    if conceptos_node is not None:
        conceptos = find_all_nodes(conceptos_node, "Concepto")
        
        # Validaciones de totales
        alertas = []
        sum_conceptos = 0.0
        try:
            subt_val = float(subtotal)
            for c in conceptos:
                try:
                    sum_conceptos += float(c.get("Importe", "0"))
                except ValueError:
                    pass
            if abs(subt_val - sum_conceptos) > 0.1:
                alertas.append(f"Subtotal ({subt_val}) no cuadra con suma de conceptos ({sum_conceptos})")
        except ValueError:
            pass
            
        estado = "Validado" if not alertas else "Requiere revision"
        alertas_str = " | ".join(alertas)
        
        for i, concepto in enumerate(conceptos, start=1):
            desc = concepto.get("Descripcion", "")
            imp_str = concepto.get("Importe", "")
            tarea = ""
            match = re.search(r'(TA-\d{3})', desc, re.IGNORECASE)
            if match:
                tarea = match.group(1).upper()
            else:
                d_lower = desc.lower()
                if "derechos, productos y aprovechamientos" in d_lower:
                    tarea = "DPA"
                elif "cuota contractual" in d_lower:
                    tarea = "Cuota Contractual"
                elif "evaluación de impacto social" in d_lower or "evaluacion de impacto social" in d_lower:
                    tarea = "EVIS"
                elif "linea base ambiental" in d_lower or "línea base ambiental" in d_lower:
                    tarea = "LBA"
                elif "geologicos regionales" in d_lower or "geológicos regionales" in d_lower:
                    tarea = "TA-012"
                elif "geologicos de detalle" in d_lower or "geológicos de detalle" in d_lower:
                    tarea = "TA-013"
                elif any(word in d_lower for word in ["metoceanico", "metoceánico", "geofisico", "geofísico", "geotecnico", "geotécnico", "geologico", "geológico"]):
                    tarea = "TA-027"
                elif "freight-truck" in d_lower or "perforacion de pozos" in d_lower or "perforación de pozos" in d_lower:
                    tarea = "TA-020"
                elif "renta de plataformas" in d_lower:
                    tarea = "TA-018"
                elif "logistica" in d_lower or "logística" in d_lower:
                    tarea = "TA-016"
                elif re.search(r'\b(arp|pre|pca)\b', d_lower):
                    tarea = "TA-025"
                elif "seguridad salud y medio ambiente" in d_lower or "seguridad, salud y medio ambiente" in d_lower or "impacto ambiental" in d_lower:
                    tarea = "TA-029"
                elif "overhead" in d_lower:
                    tarea = "Overhead"
                else:
                    tarea = desc[:50]
            
            # Si es el primer concepto, ponemos los totales. Si no, 0.00
            is_first = (i == 1)
            
            row = {
                "Folio Fiscal": folio_fiscal,
                "Serie y folio": serie_folio,
                "Fecha": fecha,
                "Año": anio,
                "Trimestre": trimestre,
                "Mes": mes,
                "Nombre Mes": nombre_mes,
                "Emisor Rfc": emisor_rfc,
                "Nombre Emisor": nombre_emisor,
                "Receptor Rfc": receptor_rfc,
                "Nombre Receptor": nombre_receptor,
                "Tipo de Comprobante": tipo_comprobante,
                "Estado": estado,
                "Moneda": moneda,
                "Forma de pago": forma_pago,
                "Metodo de pago": metodo_pago,
                "Condiciones de Pago": condiciones_pago,
                "SubTotal": subtotal_f if is_first else "0.00",
                "Iva Trasladado": iva_trasladado_f if is_first else "0.00",
                "Iva Retenido": iva_retenido_f if is_first else "0.00",
                "Total": total_f if is_first else "0.00",
                "Monto Operador": monto_operador if is_first else "0.00",
                "Monto Socio": monto_socio if is_first else "0.00",
                "Num Concepto": i,
                "Clave": concepto.get("ClaveProdServ", ""),
                "Cantidad": concepto.get("Cantidad", ""),
                "Descripcion": desc,
                "Tarea": tarea,
                "Importe": format_amount(imp_str),
                "Archivo": file_name,
                "Ruta": file_path,
                "Alertas": alertas_str if is_first else ""
            }
            conceptos_list.append(row)

    if not conceptos_list:
        # Factura sin conceptos validos
        error_row["Alertas"] = "No se encontraron conceptos"
        return [error_row]

    return conceptos_list
