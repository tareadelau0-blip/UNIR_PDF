import streamlit as st
from pypdf import PdfWriter
import io

st.set_page_config(page_title="Unidor de PDF - Contabilidad", page_icon="📄")

st.title("📄 Unidor de PDFs Efímero")
st.write("Sube tus archivos, únelos y descárgalos. **Nada se guarda en el servidor.**")

# Selector de archivos
uploaded_files = st.file_uploader("Arrastra aquí tus archivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Unir PDFs Ahora"):
        merger = PdfWriter()
        
        for pdf in uploaded_files:
            merger.append(pdf)
        
        # Guardar en memoria (no en el disco duro)
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        
        st.success("¡PDFs combinados con éxito!")
        
        # Botón de descarga
        st.download_button(
            label="📥 Descargar PDF Final",
            data=output.getvalue(),
            file_name="DOCUMENTO_COMBINADO.pdf",
            mime="application/pdf"
        )

st.info("Nota: Al cerrar esta pestaña o refrescar, los archivos se borran de la memoria automáticamente.")
