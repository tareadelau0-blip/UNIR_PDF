import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
import base64
from streamlit_sortables import sort_items

st.set_page_config(page_title="Unidor Pro con Vista Previa", layout="wide")

st.title("📄 Unidor de PDFs con Vista Previa")

# 1. Subida de archivos
uploaded_files = st.file_uploader("Sube tus archivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Diccionario de archivos
    files_dict = {f.name: f for f in uploaded_files}
    filenames = list(files_dict.keys())

    # Creamos dos columnas: Izquierda (Controles) | Derecha (Vista Previa)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("↕️ Reordenar")
        sorted_filenames = sort_items(filenames, direction="vertical")
        
        # Selección para la vista previa
        selected_file = st.selectbox("Selecciona un archivo para ver previa:", sorted_filenames)
        
        if st.button("Unir y Descargar Todo", use_container_width=True):
            merger = PdfWriter()
            for name in sorted_filenames:
                merger.append(files_dict[name])
            
            output = io.BytesIO()
            merger.write(output)
            st.success("¡PDF Generado!")
            st.download_button("📥 Descargar PDF Final", data=output.getvalue(), file_name="unido.pdf", mime="application/pdf")

    with col2:
        st.subheader("👁️ Vista Previa")
        if selected_file:
            file_data = files_dict[selected_file].getvalue()
            # Convertir a base64 para mostrar en el navegador
            base64_pdf = base64.b64encode(file_data).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

st.caption("Nota: Procesamiento 100% en memoria RAM.")
