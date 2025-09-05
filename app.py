import streamlit as st
import pandas as pd
import plotly.express as px
import io
import dataframe_image as dfi
import img2pdf
import matplotlib

# --- Configuración de la página ---
st.set_page_config(page_title="Gestor de Vacaciones Avanzado", layout="wide", initial_sidebar_state="expanded")
st.title("🏖️ Calendario de Vacaciones y Gestión de Días")
st.markdown("---")

st.sidebar.header("Opciones de Carga de Datos")
st.sidebar.write("Sube tu archivo Excel para visualizar las vacaciones de los empleados y gestionar sus días.")

# --- Componente para subir el archivo ---
uploaded_file = st.sidebar.file_uploader(
    "Elige un archivo Excel (.xlsx)",
    type="xlsx",
    help="El archivo debe contener las columnas: 'Empleado', 'Fecha_Inicio', 'Fecha_Fin' y 'Dias_Totales'."
)

def create_pdf_report(df_summary, plotly_fig):
    """
    Genera un PDF a partir de un DataFrame y una figura de Plotly.
    """
    summary_img_bytes = io.BytesIO()
    # Estilo para la tabla en la imagen
    df_styled = df_summary.style.background_gradient(cmap='viridis').set_table_styles([{
        'selector': 'th',
        'props': [('background-color', '#4CAF50'), ('color', 'white')]
    }]).format("{:.0f}")
    dfi.export(df_styled, summary_img_bytes, table_conversion='matplotlib')
    summary_img_bytes.seek(0)

    gantt_img_bytes = plotly_fig.to_image(format="png", width=1200, height=600, scale=2)
    image_list = [summary_img_bytes.getvalue(), gantt_img_bytes]
    pdf_bytes = img2pdf.convert(image_list)
    return pdf_bytes

# --- Lógica principal ---
if uploaded_file is not None:
    st.success("¡Archivo Excel cargado con éxito! 🎉")
    try:
        df = pd.read_excel(uploaded_file)

        required_cols = ['Empleado', 'Fecha_Inicio', 'Fecha_Fin', 'Dias_Totales']
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ Error: El archivo Excel debe contener todas estas columnas: {', '.join(required_cols)}")
            st.stop()

        # --- Cálculos ---
        df['Fecha_Inicio'] = pd.to_datetime(df['Fecha_Inicio'])
        df['Fecha_Fin'] = pd.to_datetime(df['Fecha_Fin'])
        df['Dias_Tomados_Periodo'] = (df['Fecha_Fin'] - df['Fecha_Inicio']).dt.days + 1

        # 1. Crear el DataFrame de resumen (único por empleado) para la tabla y el PDF
        resumen_df = df.groupby('Empleado').agg(
            Dias_Totales=('Dias_Totales', 'first'),
            Total_Dias_Tomados=('Dias_Tomados_Periodo', 'sum')
        ).reset_index()
        resumen_df['Dias_Restantes'] = resumen_df['Dias_Totales'] - resumen_df['Total_Dias_Tomados']
        
        # 2. Unir la información de los totales al DataFrame original para que cada fila la tenga
        # Esto permite que el Gantt (que usa el 'df' original) muestre los días restantes correctos al pasar el ratón
        df = pd.merge(
            df.drop(columns=['Dias_Totales']), # Quitamos Dias_Totales del original para evitar conflictos
            resumen_df, 
            on='Empleado', 
            how='left'
        )

        st.subheader("📋 Resumen de Días por Empleado")
        st.dataframe(
            resumen_df.set_index('Empleado').style.highlight_max(
                subset=['Dias_Restantes'], color='lightgreen'
            ).format("{:.0f}"),
            use_container_width=True
        )

        st.markdown("---")
        st.subheader("🗓️ Diagrama de Gantt Interactivo de Vacaciones")

        # El Gantt usará el DataFrame 'df' original, que tiene todas las entradas por separado
        fig = px.timeline(
            df,
            x_start="Fecha_Inicio",
            x_end="Fecha_Fin",
            y="Empleado",
            color="Empleado",
            text="Dias_Tomados_Periodo",
            title="Planificación de Vacaciones por Empleado",
            labels={"Fecha_Inicio": "Inicio", "Fecha_Fin": "Fin", "Empleado": "Nombre", "color": "Empleado"},
            hover_name="Empleado",
            hover_data={
                "Fecha_Inicio": "|%d %b %Y", # Formato de fecha para el hover
                "Fecha_Fin": "|%d %b %Y",
                "Dias_Tomados_Periodo": True, 
                "Dias_Totales": True, 
                "Total_Dias_Tomados": True, 
                "Dias_Restantes": True, 
                "Empleado": False
            }
        )
        fig.update_yaxes(autorange="reversed", title_text="Empleado", tickfont=dict(size=12))
        fig.update_xaxes(showgrid=True, tickformat="%d-%b", dtick="M1", rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"), dict(count=6, label="6m", step="month", stepmode="backward"), dict(count=1, label="YTD", step="year", stepmode="todate"), dict(count=1, label="1y", step="year", stepmode="backward"), dict(step="all")])), rangeslider=dict(visible=True), type="date")
        fig.update_traces(marker_line_width=1, marker_line_color='white', textposition='inside', textfont_size=12, textfont_color='black')
        fig.update_layout(title_text='Calendario Detallado de Vacaciones por Empleado', title_x=0.5, title_font_size=26, height=600, xaxis_rangeselector_font_size=12, margin=dict(l=50, r=50, t=80, b=50), legend_title_text='Empleados', font=dict(family="Arial, sans-serif", size=14, color="#333"), hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial, sans-serif"))
        
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 **Para guardar solo el gráfico:** Puedes descargarlo como una imagen PNG haciendo click en el ícono de la cámara 📷 en la esquina superior derecha del gráfico.")
        
        st.markdown("---")

        st.subheader("📥 Descargar Reporte Completo")
        st.write("Haz clic en el botón para descargar la tabla de resumen y el diagrama de Gantt en un solo archivo PDF, listo para imprimir.")
        
        pdf_bytes = create_pdf_report(resumen_df.set_index('Empleado'), fig)
        
        st.download_button(
            label="Descargar Reporte en PDF 📄",
            data=pdf_bytes,
            file_name="reporte_vacaciones.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo o en los cálculos: {e}")
        st.warning("Por favor, verifica el formato de tu archivo Excel.")

else:
    st.info("Por favor, sube un archivo Excel para comenzar.")

st.markdown("---")
st.write("Desarrollado con Streamlit y Plotly.")
