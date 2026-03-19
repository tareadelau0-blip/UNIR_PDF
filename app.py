import streamlit as st
from pypdf import PdfWriter
import io
import base64
from streamlit_sortables import sort_items

st.set_page_config(page_title="Unidor Pro - Contabilidad", layout="wide", page_icon="📄")

# Título e Instrucciones
st.title("📄 Unidor de PDFs - Vista Real")
st.write("Si el visor no carga, usa el enlace de 'Abrir Vista Previa' que aparecerá abajo.")

# Función para limpiar la sesión
def clear_session():
    for key in st.session_state.keys():
        del st.session_state[key]

# 1. Selector de archivos
uploaded_files = st.file_uploader("Sube tus archivos PDF", type="pdf", accept_multiple_files=True, key="uploader")

if uploaded_files:
    files_dict = {f.name: f for f in uploaded_files}
    filenames = list(files_dict.keys())

    col_control, col_preview = st.columns([1, 1.5])

    with col_control:
        st.subheader("↕️ Ordenar y Unir")
        # Herramienta de arrastrar
        sorted_filenames = sort_items(filenames, direction="vertical", key="sortable")
        
        st.divider()
        
        # Selección para vista previa
        selected_file = st.selectbox("🔍 Ver contenido de:", sorted_filenames)
        
        if st.button("🚀 GENERAR PDF UNIDO", use_container_width=True):
            merger = PdfWriter()
            for name in sorted_filenames:
                merger.append(files_dict[name])
            
            output = io.BytesIO()
            merger.write(output)
            merger.close()
            
            st.success("¡PDF listo!")
            st.download_button(
                label="📥 DESCARGAR RESULTADO",
                data=output.getvalue(),
                file_name="UNIDO_CONTABLE.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        if st.button("🗑️ Limpiar todo", on_click=clear_session, use_container_width=True):
            st.rerun()

    with col_preview:
        st.subheader("👁️ Visualizador")
        if selected_file:
            file_bytes = files_dict[selected_file].getvalue()
            base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
            
            # Formato compatible: Si el embed falla, el navegador mostrará un enlace de descarga automática
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
            
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # BOTÓN DE RESPALDO: Si no se ve nada en el cuadro, este botón abre el PDF en una pestaña nueva
            st.info("¿Cuadro en blanco? Haz clic abajo para ver el archivo:")
            st.download_button(
                label=f"📖 Abrir {selected_file} en ventana completa",
                data=file_bytes,
                file_name=selected_file,
                mime="application/pdf"
            )

else:
    st.info("Sube tus archivos para comenzar a trabajar.")

st.caption("Seguridad: Los archivos se procesan solo en la RAM de la sesión actual.")
