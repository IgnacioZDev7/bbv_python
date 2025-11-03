# bbv_prototipo_python/app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pdfplumber
import os
import re

# === CONFIGURACIÓN ===
st.set_page_config(page_title="BBV - Dashboard Sectorial", layout="wide")
st.title("Bolsa Boliviana de Valores - Dashboard Sectorial")
st.markdown("**Análisis financiero trimestral** | Datos oficiales de BBV")

# === SECTORES Y EMPRESAS ===
sectores_empresas = {
    "Agroindustria": ["BVC"],
    "Construcción": ["ICT"],
    "Financiero": ["BFC", "BSA"],
    "Industrial": ["PIL", "EMB"],
    "Servicios": ["UPSA", "SABSA"]
}

# === SELECCIÓN ===
col1, col2 = st.columns(2)
with col1:
    sector = st.selectbox("Selecciona un Sector", options=list(sectores_empresas.keys()))
with col2:
    empresa = st.selectbox("Selecciona una Empresa", options=sectores_empresas[sector], index=0)

CODIGO = empresa
st.subheader(f"Empresa: {empresa}")

# === CAMPOS ===
campos = [
    'total_activo_corriente', 'total_activo_no_corriente', 'total_activo',
    'total_pasivo_corriente', 'total_pasivo_no_corriente', 'total_pasivo',
    'total_patrimonio'
]
nombres_bonitos = {
    'total_activo_corriente': 'Activo Corriente',
    'total_activo_no_corriente': 'Activo No Corriente',
    'total_activo': 'Total Activo',
    'total_pasivo_corriente': 'Pasivo Corriente',
    'total_pasivo_no_corriente': 'Pasivo No Corriente',
    'total_pasivo': 'Total Pasivo',
    'total_patrimonio': 'Patrimonio Neto'
}

# === CÓDIGOS POR EMPRESA ===
codigos = {
    "BVC": {
        'total_activo_corriente': '12490',
        'total_activo_no_corriente': '12990',
        'total_pasivo_corriente': '22490',
        'total_pasivo_no_corriente': '22990',
    },
    "ICT": {
        'total_activo_corriente': '10990',
        'total_activo_no_corriente': '19990',
        'total_pasivo_corriente': '20990',
        'total_pasivo_no_corriente': '29990',
    }
}

# === EXTRAER DATOS POR TABLAS (INTELIGENTE) ===
def extraer_datos_pdf(pdf_path, empresa):
    datos = {campo: 0.0 for campo in campos}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row or len(row) < 2:
                            continue
                        codigo_cell = str(row[0]).strip() if row[0] else ""
                        valor_cell = str(row[-1]).strip() if row[-1] else ""
                        
                        # Limpiar valor
                        valor_str = re.sub(r'[^\d,\.]', '', valor_cell)
                        if not valor_str:
                            continue
                        try:
                            valor = float(valor_str.replace('.', '').replace(',', '.'))
                        except:
                            continue
                        
                        # BVC: por código
                        if empresa == "BVC":
                            if codigo_cell == codigos["BVC"]['total_activo_corriente']:
                                datos['total_activo_corriente'] = valor
                            elif codigo_cell == codigos["BVC"]['total_activo_no_corriente']:
                                datos['total_activo_no_corriente'] = valor
                            elif codigo_cell == codigos["BVC"]['total_pasivo_corriente']:
                                datos['total_pasivo_corriente'] = valor
                            elif codigo_cell == codigos["BVC"]['total_pasivo_no_corriente']:
                                datos['total_pasivo_no_corriente'] = valor
                        
                        # ICT: por código
                        elif empresa == "ICT":
                            if codigo_cell == codigos["ICT"]['total_activo_corriente']:
                                datos['total_activo_corriente'] = valor
                            elif codigo_cell == codigos["ICT"]['total_activo_no_corriente']:
                                datos['total_activo_no_corriente'] = valor
                            elif codigo_cell == codigos["ICT"]['total_pasivo_corriente']:
                                datos['total_pasivo_corriente'] = valor
                            elif codigo_cell == codigos["ICT"]['total_pasivo_no_corriente']:
                                datos['total_pasivo_no_corriente'] = valor
                        
                        # Totales por texto
                        row_text = ' '.join([str(cell) for cell in row if cell]).upper()
                        if 'TOTAL ACTIVO' in row_text and 'CORRIENTE' not in row_text:
                            datos['total_activo'] = valor
                        elif 'TOTAL PASIVO' in row_text:
                            datos['total_pasivo'] = valor
                        elif 'TOTAL PATRIMONIO' in row_text:
                            datos['total_patrimonio'] = valor
                            
    except Exception as e:
        st.error(f"Error en {os.path.basename(pdf_path)}: {e}")
    
    return datos

# === PROCESAR PDFs ===
if st.button(f"Procesar PDFs de {CODIGO} (scripts/pdfs/{CODIGO}/)"):
    base_dir = os.path.join("scripts", "pdfs", CODIGO)
    if not os.path.exists(base_dir):
        st.error(f"No existe: {base_dir}")
        st.stop()
    
    datos_lista = []
    for año_dir in os.listdir(base_dir):
        año_path = os.path.join(base_dir, año_dir)
        if not os.path.isdir(año_path) or not año_dir.isdigit():
            continue
        
        for q_dir in os.listdir(año_path):
            q_path = os.path.join(año_path, q_dir)
            if not os.path.isdir(q_path):
                continue
            
            pdf_files = [f for f in os.listdir(q_path) if f.upper().endswith('.PDF')]
            if not pdf_files:
                continue
            
            pdf_file = pdf_files[0]
            pdf_path = os.path.join(q_path, pdf_file)
            
            match = re.search(r'(\d{4})(\d{2})', pdf_file)
            if not match:
                continue
            año, mes = match.groups()
            fecha = f"{año}-{mes}-30"
            
            datos = extraer_datos_pdf(pdf_path, CODIGO)
            if datos['total_activo'] == 0:
                st.warning(f"Sin datos: {pdf_file}")
                continue
            
            fila = {'fecha': fecha, **datos}
            datos_lista.append(fila)
    
    if not datos_lista:
        st.error("No se extrajeron datos válidos.")
        st.stop()
    
    df = pd.DataFrame(datos_lista)
    for campo in campos:
        if campo not in df.columns:
            df[campo] = 0.0
        df[campo] = pd.to_numeric(df[campo], errors='coerce').fillna(0) * 1000
    
    df['fecha'] = pd.to_datetime(df['fecha'])
    df = df.sort_values('fecha').reset_index(drop=True)
    
    os.makedirs("datos", exist_ok=True)
    df.to_csv(f"datos/{CODIGO.lower()}_datos_limpios.csv", sep=';', index=False)
    st.success(f"¡Listo! {len(df)} trimestres procesados.")

# === CARGAR DATOS ===
@st.cache_data
def cargar_datos():
    path = f"datos/{CODIGO.lower()}_datos_limpios.csv"
    if os.path.exists(path):
        df = pd.read_csv(path, sep=';', parse_dates=['fecha'])
        for campo in campos:
            if campo not in df.columns:
                df[campo] = 0.0
            df[campo] = pd.to_numeric(df[campo], errors='coerce').fillna(0)
        return df.sort_values('fecha')
    return None

df = cargar_datos()
if df is None:
    st.info(f"Presiona **'Procesar PDFs de {CODIGO}'** para cargar los datos.")
    st.stop()

# === FILTROS ===
st.sidebar.header("Filtros")
campos_seleccionados = st.sidebar.multiselect(
    "Campos para graficar",
    options=campos,
    default=['total_activo', 'total_pasivo', 'total_patrimonio'],
    format_func=lambda x: nombres_bonitos[x]
)

fecha_min = df['fecha'].min().date()
fecha_max = df['fecha'].max().date()
fecha_inicio = st.sidebar.date_input("Fecha inicio", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
fecha_fin = st.sidebar.date_input("Fecha fin", value=fecha_max, min_value=fecha_min, max_value=fecha_max)
if fecha_inicio > fecha_fin:
    st.sidebar.error("Fecha inicio debe ser menor o igual a fecha fin.")
    st.stop()

df_filtrado = df[(df['fecha'] >= pd.Timestamp(fecha_inicio)) & (df['fecha'] <= pd.Timestamp(fecha_fin))]

# === MÉTRICAS ===
st.subheader("Métricas del Último Trimestre")
if len(df_filtrado) == 0:
    st.info("No hay datos en el rango seleccionado.")
    st.stop()

ultimo = df_filtrado.iloc[-1]
cols = st.columns(3)
# Mostrar métricas básicas siempre; se podrían condicionar a la selección si se desea
cols[0].metric("Total Activo", f"Bs {ultimo['total_activo']/1e6:.1f}M")
cols[1].metric("Total Pasivo", f"Bs {ultimo['total_pasivo']/1e6:.1f}M")
cols[2].metric("Patrimonio Neto", f"Bs {ultimo['total_patrimonio']/1e6:.1f}M")

# === GRÁFICO 1: EVOLUCIÓN FINANCIERA (EJE DOBLE) ===
st.subheader(f"Evolución Financiera - {CODIGO} ({df_filtrado['fecha'].min().strftime('%Y Q%m')[5:]} → {df_filtrado['fecha'].max().strftime('%Y Q%m')[5:]})")
st.markdown("**Activo y Pasivo (izq) | Patrimonio (der)**")

# Construir gráfico 1 respetando los campos seleccionados
time_series_fields = ['total_activo', 'total_pasivo', 'total_patrimonio']
colors_time = {'total_activo': '#1f77b4', 'total_pasivo': '#d62728', 'total_patrimonio': '#2ca02c'}

fig1 = go.Figure()
for campo in campos_seleccionados:
    if campo in time_series_fields:
        trace_kwargs = dict(x=df_filtrado['fecha'], y=df_filtrado[campo]/1e6,
                            mode='lines+markers', name=nombres_bonitos.get(campo, campo),
                            line=dict(color=colors_time.get(campo, '#888'), width=3), marker=dict(size=6))
        # Patrimonio en eje secundario
        if campo == 'total_patrimonio':
            trace_kwargs['yaxis'] = 'y2'
        else:
            trace_kwargs['yaxis'] = 'y'
        fig1.add_trace(go.Scatter(**trace_kwargs))

fig1.update_layout(
    xaxis=dict(title="Fecha"),
    yaxis=dict(title="Activo y Pasivo (Millones Bs)", side="left"),
    yaxis2=dict(title="Patrimonio Neto (Millones Bs)", side="right", overlaying="y"),
    legend=dict(x=0.01, y=0.99),
    hovermode="x unified",
    height=600,
    template="plotly_dark"
)

# Si el usuario no seleccionó ninguna serie de tiempo, mostrar un mensaje
if not any(f in time_series_fields for f in campos_seleccionados):
    st.info("Selecciona alguna serie (Total Activo, Total Pasivo o Patrimonio) en los filtros para ver la evolución financiera.")
else:
    st.plotly_chart(fig1, use_container_width=True)

# === GRÁFICO 2: ESTRUCTURA DEL ACTIVO ===
# Gráfico 2: Estructura del Activo (respetando selección de campos)
activo_components = ['total_activo_corriente', 'total_activo_no_corriente']
seleccion_activo = [c for c in campos_seleccionados if c in activo_components]
if seleccion_activo:
    st.subheader("Estructura del Activo")
    df_activo = df_filtrado.melt(id_vars='fecha', value_vars=seleccion_activo,
                                 var_name='Tipo', value_name='Valor')
    df_activo['Tipo'] = df_activo['Tipo'].map(nombres_bonitos)
    df_activo['Valor'] /= 1e6
    df_activo['Trimestre'] = df_activo['fecha'].dt.strftime('%Y-%m')
    orden_trimestres = df_filtrado['fecha'].dt.strftime('%Y-%m').tolist()

    # Si hay más de una serie, usar apilado; si solo una, mostrar barras simples
    barmode = 'stack' if len(seleccion_activo) > 1 else 'group'
    color_map = {'Activo Corriente': '#17becf', 'Activo No Corriente': '#1f77b4'}
    fig2 = px.bar(
        df_activo,
        x='Trimestre',
        y='Valor',
        color='Tipo' if len(seleccion_activo) > 1 else None,
        barmode=barmode,
        category_orders={'Trimestre': orden_trimestres},
        color_discrete_map=color_map
    )
    fig2.update_layout(xaxis_title="Trimestre", yaxis_title="Millones Bs", height=500, template="plotly_dark", bargap=0.12)
    st.plotly_chart(fig2, use_container_width=True)

# === GRÁFICO 3: TENDENCIA DEL PATRIMONIO ===
st.subheader("Tendencia del Patrimonio Neto")
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=df_filtrado['fecha'], y=df_filtrado['total_patrimonio']/1e6,
                          mode='lines+markers', name='Patrimonio Real',
                          line=dict(color='#2ca02c', width=3)))
if len(df_filtrado) > 1:
    x_num = np.arange(len(df_filtrado))
    z = np.polyfit(x_num, df_filtrado['total_patrimonio'], 1)
    p = np.poly1d(z)
    fig3.add_trace(go.Scatter(x=df_filtrado['fecha'], y=p(x_num)/1e6,
                              mode='lines', name='Tendencia',
                              line=dict(color='red', dash='dash', width=2)))
fig3.update_layout(xaxis_title="Trimestre", yaxis_title="Millones Bs", height=500, template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

# === TABLA ===
st.subheader("Datos Completos")
# Si el usuario no seleccionó campos, mostrar todas las columnas definidas en `campos`
if not campos_seleccionados:
    mostrar_campos = campos
else:
    mostrar_campos = campos_seleccionados

st.dataframe(df_filtrado[['fecha'] + mostrar_campos].style.format({c: 'Bs {:,.0f}' for c in mostrar_campos}), use_container_width=True)

# === DESCARGA ===
csv = df_filtrado.to_csv(index=False, sep=';').encode('utf-8')
st.download_button("Descargar", csv, f"{CODIGO.lower()}_datos.csv", "text/csv")