import streamlit as st
from pypdf import PdfWriter
import io
import base64
from streamlit_sortables import sort_items

# Configuración de la página en modo ancho para ver bien la previa
st.set_page_config(page_title="Unidor Pro - Vista Previa", layout="wide", page_icon="📄")

# Estilo personalizado para mejorar la visibilidad
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 Unidor de PDFs Contable")
st.write("Sube tus documentos, ordénalos visualmente y genera el anexo final.")

# 1. Selector de archivos
uploaded_files = st.file_uploader("Arrastra aquí tus archivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Creamos un diccionario para referenciar los archivos por nombre
    files_dict = {f.name: f for f in uploaded_files}
    filenames = list(files_dict.keys())

    # Dividimos la pantalla en dos columnas
    col_control, col_preview = st.columns([1, 1.2])

    with col_control:
        st.subheader("↕️ Orden de Unión")
        st.info("Arrastra los nombres para cambiar la posición:")
        
        # Herramienta para reordenar arrastrando
        sorted_filenames = sort_items(filenames, direction="vertical")
        
        st.divider()
        
        # Selector para decidir qué archivo ver a la derecha
        selected_file = st.selectbox("🔍 Seleccionar para vista previa:", sorted_filenames)
        
        st.divider()
        
        # Botón para procesar todo
        if st.button("🚀 UNIR Y DESCARGAR TODO"):
            with st.spinner("Generando PDF combinado en la RAM..."):
                merger = PdfWriter()
                for name in sorted_filenames:
                    merger.append(files_dict[name])
                
                # Guardar resultado en memoria
                output = io.BytesIO()
                merger.write(output)
                merger.close()
                
                st.success("¡Documento generado con éxito!")
                st.download_button(
                    label="📥 Guardar PDF Final",
                    data=output.getvalue(),
                    file_name="REPORTE_COMBINADO.pdf",
                    mime="application/pdf"
                )

    with col_preview:
        st.subheader("👁️ Vista Previa del Documento")
        if selected_file:
            # Extraer datos del archivo seleccionado
            file_bytes = files_dict[selected_file].getvalue()
            base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
            
            # Formato de visualización con soporte para la mayoría de navegadores
            pdf_display = f'''
                <div style="border: 1px solid #ccc; border-radius: 10px; overflow: hidden;">
                    <embed src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0&scrollbar=0" 
                           width="100%" 
                           height="750" 
                           type="application/pdf"
                           style="border: none;">
                </div>
            '''
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Enlace de emergencia si el navegador bloquea el objeto
            st.caption("¿No ves la previa? [Haz clic aquí para abrir en pestaña nueva](data:application/pdf;base64," + base64_pdf + ")")

else:
    st.warning("Esperando archivos... Sube tus facturas o anexos para comenzar.")

st.divider()
st.caption("Seguridad: Esta herramienta no guarda archivos en disco. Todo se procesa en la memoria RAM y se borra al cerrar el navegador.")
