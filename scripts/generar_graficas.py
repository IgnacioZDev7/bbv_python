import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np  # ← AÑADIDO AQUÍ
import os
from matplotlib.ticker import FuncFormatter

# === CONFIGURACIÓN ===
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 9)
plt.rcParams['font.size'] = 13
plt.rcParams['axes.titlesize'] = 18
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 11
plt.rcParams['ytick.labelsize'] = 11
plt.rcParams['legend.fontsize'] = 12

# Colores
COLOR_ACTIVO = '#1f77b4'      # Azul
COLOR_PASIVO = '#d62728'      # Rojo
COLOR_PATRIMONIO = '#2ca02c'  # Verde

# Rutas
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS_DIR = os.path.join(ROOT_DIR, 'datos')
GRAFICOS_DIR = os.path.join(ROOT_DIR, 'graficos')
os.makedirs(GRAFICOS_DIR, exist_ok=True)

# Formateador
def millones(x, pos):
    return f'{x/1e6:.1f}M'

formatter = FuncFormatter(millones)

# === CARGAR DATOS ===
def cargar_datos():
    path = os.path.join(DATOS_DIR, 'bvc_datos_limpios.csv')
    df = pd.read_csv(path, sep=';', parse_dates=['fecha'])
    df = df.sort_values('fecha').reset_index(drop=True)
    print(f"Generando gráficos con {len(df)} trimestres")
    return df

# === GRÁFICO 1: EVOLUCIÓN COMPARATIVA (DOS EJES Y) ===
def grafico_comparativo_dos_ejes(df):
    fig, ax1 = plt.subplots()

    # Eje Y1: Activo y Pasivo
    ax1.plot(df['fecha'], df['total_activo'], 'o-', color=COLOR_ACTIVO, linewidth=3, markersize=7, label='Total Activo')
    ax1.plot(df['fecha'], df['total_pasivo'], 's-', color=COLOR_PASIVO, linewidth=3, markersize=7, label='Total Pasivo')
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('Activo / Pasivo (Bs)', color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.yaxis.set_major_formatter(formatter)

    # Eje Y2: Patrimonio
    ax2 = ax1.twinx()
    ax2.plot(df['fecha'], df['total_patrimonio'], '^-', color=COLOR_PATRIMONIO, linewidth=3, markersize=8, label='Patrimonio Neto')
    ax2.set_ylabel('Patrimonio Neto (Bs)', color=COLOR_PATRIMONIO)
    ax2.tick_params(axis='y', labelcolor=COLOR_PATRIMONIO)
    ax2.yaxis.set_major_formatter(formatter)

    # Título y leyenda
    plt.title('Evolución Financiera - BVC (2020 Q1 → 2023 Q3)\nActivo y Pasivo (izq) | Patrimonio (der)', 
              fontweight='bold', pad=20)
    
    # Leyenda combinada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # Fechas espaciadas
    plt.xticks(df['fecha'], [d.strftime('%Y-%m') for d in df['fecha']], rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(True, alpha=0.3)

    filename = 'evolucion_comparativa_bvc_2020_2023_DOS_EJES.png'
    plt.savefig(os.path.join(GRAFICOS_DIR, filename), dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Guardado: {filename}")

# === GRÁFICO 2: TENDENCIA PATRIMONIO (FECHAS CLARAS) ===
def grafico_patrimonio_tendencia(df):
    plt.figure()
    
    # Puntos y línea
    plt.plot(df['fecha'], df['total_patrimonio'], 'o-', color=COLOR_PATRIMONIO, 
             linewidth=3, markersize=8, label='Patrimonio Real')
    
    # Línea de tendencia
    z = np.polyfit(range(len(df)), df['total_patrimonio'], 1)
    p = np.poly1d(z)
    plt.plot(df['fecha'], p(range(len(df))), "--", color='red', linewidth=2, label='Tendencia')

    plt.title('Tendencia del Patrimonio Neto - BVC (2020-2023)', fontweight='bold', pad=20)
    plt.xlabel('Fecha')
    plt.ylabel('Patrimonio (Bs)')
    plt.gca().yaxis.set_major_formatter(formatter)
    plt.xticks(df['fecha'], [d.strftime('%Y-%m') for d in df['fecha']], rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    filename = 'tendencia_patrimonio_bvc_FECHAS_CLARAS.png'
    plt.savefig(os.path.join(GRAFICOS_DIR, filename), dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Guardado: {filename}")

# === GRÁFICO 3: ESTRUCTURA ACTIVO (MEJORADO) ===
def grafico_estructura(df):
    plt.figure()
    width = 0.35
    x = range(len(df))
    
    plt.bar([i - width/2 for i in x], df['total_activo_corriente']/1e6, width, 
            label='Activo Corriente', color='#17becf', alpha=0.9)
    plt.bar([i + width/2 for i in x], df['total_activo_no_corriente']/1e6, width, 
            label='Activo No Corriente', color=COLOR_ACTIVO, alpha=0.9)
    
    plt.title('Estructura del Activo - BVC (2020-2023)', fontweight='bold')
    plt.xlabel('Trimestre')
    plt.ylabel('Valor (millones Bs)')
    plt.xticks(x, [f"{d.strftime('%Y-%m')}" for d in df['fecha']], rotation=45, ha='right')
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()

    filename = 'estructura_activo_bvc_MEJORADO.png'
    plt.savefig(os.path.join(GRAFICOS_DIR, filename), dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Guardado: {filename}")

# === EJECUCIÓN ===
if __name__ == "__main__":
    df = cargar_datos()
    grafico_comparativo_dos_ejes(df)
    grafico_patrimonio_tendencia(df)
    grafico_estructura(df)
    
    print("\nTODOS LOS GRÁFICOS CORREGIDOS GENERADOS")
    print("   • Línea azul ahora visible")
    print("   • Fechas claras")
    print("   • Tendencia perfecta")