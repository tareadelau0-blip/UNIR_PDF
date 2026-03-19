import streamlit as st
from pypdf import PdfWriter
import io
from streamlit_sortables import sort_items

# Configuración compacta
st.set_page_config(page_title="Unidor PDF Express", page_icon="📄")

# Estética Profesional (Oscura/Minimalista como te gusta)
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    .stButton>button { width: 100%; background-color: #2c2c2c; color: white; border: 1px solid #444; }
    .stButton>button:hover { background-color: #444; border-color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 Unidor de PDFs Contable")
st.write("Herramienta rápida para anexos y partidas. Procesamiento 100% en RAM.")

# Función para resetear la aplicación
if st.button("🗑️ Limpiar y Nueva Unión"):
    st.session_state.clear()
    st.rerun()

st.divider()

# 1. Zona de carga
uploaded_files = st.file_uploader("Arrastra tus archivos aquí", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Diccionario para manejar los archivos
    files_dict = {f.name: f for f in uploaded_files}
    filenames = list(files_dict.keys())

    st.subheader("↕️ Ordenar archivos")
    st.caption("Arrastra los nombres para definir el orden final del documento:")
    
    # Interfaz de arrastrar y soltar
    sorted_filenames = sort_items(filenames, direction="vertical", key="sort_pdf_list")

    st.divider()

    # 2. Botón de Procesamiento
    if st.button("🚀 UNIR Y DESCARGAR PDF"):
        with st.spinner("Combinando documentos..."):
            try:
                merger = PdfWriter()
                for name in sorted_filenames:
                    merger.append(files_dict[name])
                
                # Crear el PDF en memoria
                output = io.BytesIO()
                merger.write(output)
                merger.close()
                
                st.success("¡Unión completada!")
                
                # Botón de descarga
                st.download_button(
                    label="💾 Guardar Archivo Combinado",
                    data=output.getvalue(),
                    file_name="ANEXO_COMBINADO.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error al unir: {e}")

else:
    st.info("Sube los archivos PDF que deseas combinar para habilitar el ordenamiento.")

st.divider()
st.caption("Seguridad: Esta herramienta es efímera. Al cerrar la pestaña, los datos desaparecen de la memoria del servidor.")
