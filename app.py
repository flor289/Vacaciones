import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# --- Configuración de la página ---
st.set_page_config(page_title="Gantt de Vacaciones", layout="wide")
st.title("📊 Diagrama de Gantt para Vacaciones")
st.write("Esta aplicación lee un archivo Excel para visualizar las vacaciones de los empleados y calcular los días restantes.")

# --- Carga y Procesamiento de Datos ---
try:
    # Cargar los datos desde el archivo Excel
    df = pd.read_excel("vacaciones.xlsx")

    # --- Cálculos ---
    # 1. Convertir las columnas de fecha a formato de fecha real
    df['Fecha_Inicio'] = pd.to_datetime(df['Fecha_Inicio'])
    df['Fecha_Fin'] = pd.to_datetime(df['Fecha_Fin'])

    # 2. Calcular los días tomados en cada período de vacaciones (incluyendo el día de inicio)
    df['Dias_Tomados_Periodo'] = (df['Fecha_Fin'] - df['Fecha_Inicio']).dt.days + 1

    # 3. Calcular el total de días tomados por cada empleado (sumando todos sus períodos)
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
        # Información que aparece al pasar el mouse sobre una barra
        hover_data={
            "Dias_Tomados_Periodo": True,
            "Dias_Restantes": True
        }
    )

    # Mejorar la visualización
    fig.update_yaxes(autorange="reversed") # Para que los empleados aparezcan en orden
    fig.update_layout(
        title_font_size=24,
        font_size=14,
        xaxis_title="Fecha",
        yaxis_title="Empleado"
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)


except FileNotFoundError:
    st.error("❌ **Error:** No se encontró el archivo `vacaciones.xlsx`. Asegúrate de que el archivo esté en la misma carpeta que la aplicación.")
except Exception as e:
    st.error(f"Ocurrió un error al procesar el archivo: {e}")