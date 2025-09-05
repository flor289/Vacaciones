import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración de la página ---
st.set_page_config(page_title="Gantt de Vacaciones", layout="wide")
st.title("📊 Diagrama de Gantt para Vacaciones")
st.write("Sube tu archivo Excel para visualizar las vacaciones de los empleados y calcular los días restantes.")

# --- Componente para subir el archivo ---
# Se crea un espacio para que el usuario suba su archivo
uploaded_file = st.file_uploader(
    "Elige un archivo Excel (.xlsx)", 
    type="xlsx"
)

# --- Lógica principal ---
# El código solo se ejecuta si el usuario ha subido un archivo
if uploaded_file is not None:
    st.success("¡Archivo cargado con éxito!")

    try:
        # Cargar los datos desde el archivo Excel que el usuario subió
        df = pd.read_excel(uploaded_file)

        # --- Cálculos ---
        # 1. Convertir las columnas de fecha a formato de fecha real
        df['Fecha_Inicio'] = pd.to_datetime(df['Fecha_Inicio'])
        df['Fecha_Fin'] = pd.to_datetime(df['Fecha_Fin'])

        # 2. Calcular los días tomados en cada período de vacaciones
        df['Dias_Tomados_Periodo'] = (df['Fecha_Fin'] - df['Fecha_Inicio']).dt.days + 1

        # 3. Calcular el total de días tomados por cada empleado
        total_tomados_por_empleado = df.groupby('Empleado')['Dias_Tomados_Periodo'].sum().to_dict()
        df['Total_Dias_Tomados'] = df['Empleado'].map(total_tomados_por_empleado)
        
        # 4. Calcular los días restantes
        df['Dias_Restantes'] = df['Dias_Totales'] - df['Total_Dias_Tomados']
        
        st.write("### Vista de Datos Cargados y Calculados")
        st.dataframe(df)

        # --- Creación del Gráfico Gantt ---
        st.write("### Diagrama de Gantt")
        
        fig = px.timeline(
            df,
            x_start="Fecha_Inicio",
            x_end="Fecha_Fin",
            y="Empleado",
            color="Empleado",
            title="Planificación de Vacaciones",
            hover_data={
                "Dias_Tomados_Periodo": True,
                "Dias_Restantes": True
            }
        )

        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            title_font_size=24,
            font_size=14,
            xaxis_title="Fecha",
            yaxis_title="Empleado"
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}. Asegúrate de que las columnas se llamen 'Empleado', 'Fecha_Inicio', 'Fecha_Fin' y 'Dias_Totales'.")

else:
    st.info("Esperando a que subas un archivo Excel.")
