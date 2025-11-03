import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS_DIR = os.path.join(ROOT_DIR, 'datos')

def limpiar_datos():
    csv_path = os.path.join(DATOS_DIR, 'bvc_estados_financieros.csv')
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró {csv_path}. Ejecuta convertir_pdf.py")

    df = pd.read_csv(csv_path, sep=';')
    print(f"Datos crudos: {len(df)} filas")

    # === 1. Eliminar filas sin total_activo ===
    df = df.dropna(subset=['total_activo'])
    df = df[df['total_activo'] > 0]

    # === 2. Convertir a bolivianos (x1000) ===
    campos = [
        'total_activo_corriente', 'total_activo_no_corriente', 'total_activo',
        'total_pasivo_corriente', 'total_pasivo_no_corriente', 'total_pasivo',
        'total_patrimonio'
    ]
    for campo in campos:
        df[campo] = pd.to_numeric(df[campo], errors='coerce') * 1000

    # === 3. Parsear fecha ===
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])

    # === 4. Filtrar rango 2020-2023 ===
    df = df[(df['fecha'] >= '2020-03-31') & (df['fecha'] <= '2023-09-30')]

    # === 5. Eliminar duplicados ===
    df = df.drop_duplicates(subset=['fecha'])

    # === 6. Ordenar ===
    df = df.sort_values('fecha').reset_index(drop=True)

    # === 7. Columnas finales ===
    columnas_finales = campos + ['fecha', 'año', 'trimestre']
    df_final = df[columnas_finales].copy()

    # === 8. Guardar ===
    output_path = os.path.join(DATOS_DIR, 'bvc_datos_limpios.csv')
    df_final.to_csv(output_path, index=False, sep=';')
    print(f"Limpieza completada: {len(df_final)} trimestres")
    print(f"Guardado: {output_path}")
    print(df_final[['fecha', 'total_activo', 'total_patrimonio']].head())

    return df_final

if __name__ == "__main__":
    limpiar_datos()