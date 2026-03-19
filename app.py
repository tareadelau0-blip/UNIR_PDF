import streamlit as st
from pypdf import PdfWriter
import io
from streamlit_sortables import sort_items

st.set_page_config(page_title="Unidor Pro - Orden Manual", page_icon="📄")

st.title("📄 Unidor de PDFs con Orden Manual")
st.write("1. Sube tus PDFs. 2. Arrástralos para reordenar. 3. Únelos.")

# Selector de archivos
uploaded_files = st.file_uploader("Sube tus archivos PDF aquí", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Creamos un diccionario para identificar cada archivo por su nombre
    files_dict = {f.name: f for f in uploaded_files}
    filenames = list(files_dict.keys())

    st.write("### ↕️ Arrastra los nombres para cambiar el orden:")
    
    # Esta es la herramienta mágica para arrastrar y soltar
    sorted_filenames = sort_items(filenames, direction="vertical")

    if st.button("Unir y Descargar PDF Final"):
        with st.spinner("Generando PDF combinado..."):
            merger = PdfWriter()
            
            # Unimos siguiendo el nuevo orden manual
            for name in sorted_filenames:
                merger.append(files_dict[name])
            
            # Guardar en memoria RAM
            output = io.BytesIO()
            merger.write(output)
            merger.close()
            
            st.success("¡Listo! El PDF se unió en el orden que elegiste.")
            
            st.download_button(
                label="📥 Descargar Resultado",
                data=output.getvalue(),
                file_name="PDF_COMBINADO_MANUAL.pdf",
                mime="application/pdf"
            )

st.caption("Nota: Los archivos se procesan en memoria y se borran al cerrar la pestaña.")
