import pdfplumber
import pandas as pd
import os
import re
from descargar_pdfs import descargar_todos_pdfs

# Rutas
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS_DIR = os.path.join(ROOT_DIR, 'datos')
os.makedirs(DATOS_DIR, exist_ok=True)

def extraer_fecha_texto(pdf_path):
    """Extrae la fecha del texto del PDF (al 30 de septiembre de 2023)"""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            # Busca: "al 30 de septiembre de 2023" o "al 30 de JUNIO de 2025"
            match = re.search(r'al\s+(\d{1,2})\s+de\s+([^\d]+)\s+de\s+(\d{4})', text, re.IGNORECASE)
            if match:
                dia = match.group(1).zfill(2)
                mes_nombre = match.group(2).strip().lower()
                año = match.group(3)
                meses = {
                    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
                }
                mes = meses.get(mes_nombre, '01')
                return f"{año}-{mes}-{dia}"
    return None

def extraer_totales(pdf_path):
    """Extrae los 7 totales clave del PDF (funciona para BVC e ICT)"""
    datos = {
        'total_activo_corriente': 0.0,
        'total_activo_no_corriente': 0.0,
        'total_activo': 0.0,
        'total_pasivo_corriente': 0.0,
        'total_pasivo_no_corriente': 0.0,
        'total_pasivo': 0.0,
        'total_patrimonio': 0.0
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            for line in lines:
                line_upper = line.upper()
                # Busca líneas que contengan "TOTAL" y un número
                if 'TOTAL' in line_upper:
                    # Extrae todos los números
                    numeros = re.findall(r'[\d\.,]+', line)
                    if numeros:
                        valor = float(numeros[-1].replace(',', '').replace('.', ''))
                        if 'ACTIVO CORRIENTE' in line_upper:
                            datos['total_activo_corriente'] = valor
                        elif 'ACTIVO NO CORRIENTE' in line_upper or 'NO CORRIENTE' in line_upper:
                            datos['total_activo_no_corriente'] = valor
                        elif 'TOTAL ACTIVO' in line_upper and 'CORRIENTE' not in line_upper:
                            datos['total_activo'] = valor
                        elif 'PASIVO CORRIENTE' in line_upper:
                            datos['total_pasivo_corriente'] = valor
                        elif 'PASIVO NO CORRIENTE' in line_upper or 'NO CORRIENTE' in line_upper:
                            datos['total_pasivo_no_corriente'] = valor
                        elif 'TOTAL PASIVO' in line_upper and 'CORRIENTE' not in line_upper:
                            datos['total_pasivo'] = valor
                        elif 'TOTAL PATRIMONIO' in line_upper or 'PATRIMONIO' in line_upper:
                            datos['total_patrimonio'] = valor
    return datos

def convertir_a_csv(paths):
    datos_lista = []
    for info in paths:
        pdf_path = info['path']
        print(f"Procesando: {os.path.basename(pdf_path)}")
        
        fecha = extraer_fecha_texto(pdf_path)
        totales = extraer_totales(pdf_path)
        
        if not fecha:
            print(f"  Fecha no encontrada en {pdf_path}")
            continue
        
        fila = {
            'fecha': fecha,
            'año': info['año'],
            'trimestre': info['trimestre'],
            **totales
        }
        datos_lista.append(fila)
    
    df = pd.DataFrame(datos_lista)
    csv_path = os.path.join(DATOS_DIR, 'bvc_estados_financieros.csv')
    df.to_csv(csv_path, index=False, sep=';')
    print(f"\nCSV guardado: {csv_path}")
    print(f"Total filas: {len(df)}")
    return df

if __name__ == "__main__":
    paths = descargar_todos_pdfs()
    df = convertir_a_csv(paths)