import requests
import os
from datetime import datetime

# Configuración
CODIGO_EMPRESA = 'BVC'  # Código para La Concepción S.A.
BASE_URL = 'https://www.bbv.com.bo/EEFF2/{}/Estados Financieros Trimestrales/Gestion {}/Trimestre {}/'.format(CODIGO_EMPRESA, '{año}', '{trimestre}')
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}  # Para evitar bloqueos

# Meses por trimestre (para nombre de archivo: 03=Q1, 06=Q2, etc.)
MESES = {1: '03', 2: '06', 3: '09', 4: '12'}

def descargar_pdf(año, trimestre):
    """Descarga un PDF específico si existe."""
    mes = MESES[trimestre]
    nombre_archivo = f"{año}{mes}_{CODIGO_EMPRESA}_EEFF_BG.PDF"
    url = BASE_URL.format(año=año, trimestre=trimestre) + nombre_archivo
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        # Crea directorio si no existe
        dir_pdf = f"pdfs/{CODIGO_EMPRESA}/{año}/Q{trimestre}"
        os.makedirs(dir_pdf, exist_ok=True)
        path = os.path.join(dir_pdf, nombre_archivo)
        with open(path, 'wb') as f:
            f.write(response.content)
        print(f"Descargado: {path} (Fecha aprox: {año}-{mes}-30)")
        return path
    else:
        print(f"No disponible: {url} (Status: {response.status_code})")
        return None

def descargar_todos_pdfs(desde_año=2020, hasta_año=2023):
    """Descarga todos los trimestres desde 2020 Q1 hasta 2023 Q3."""
    os.makedirs(f"pdfs/{CODIGO_EMPRESA}", exist_ok=True)
    paths = []
    for año in range(desde_año, hasta_año + 1):
        max_trim = 4 if año < 2023 else 3  # Solo hasta Q3 en 2023
        for trimestre in range(1, max_trim + 1):
            path = descargar_pdf(año, trimestre)
            if path:
                paths.append({
                    'año': año,
                    'trimestre': trimestre,
                    'fecha_aprox': f"{año}-{MESES[trimestre]}-30",
                    'path': path
                })
    print(f"\nResumen: {len(paths)} PDFs descargados de {len(paths)} intentados.")
    return paths

if __name__ == "__main__":
    # Ejecuta la descarga
    paths = descargar_todos_pdfs()
    print("Paths descargados:", paths)