import streamlit as st
from pypdf import PdfWriter, PdfReader, PdfWriter
import io
from streamlit_sortables import sort_items
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

st.set_page_config(page_title="Unidor con Foliado", page_icon="🔢")

# Estética Minimalista Oscura
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    .stButton>button { width: 100%; background-color: #2c2c2c; color: white; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 Unidor y Foliador de PDFs")

if st.button("🗑️ Nueva Unión / Limpiar"):
    st.session_state.clear()
    st.rerun()

st.divider()

# 1. Configuración de numeración
col_num1, col_num2 = st.columns(2)
with col_num1:
    start_number = st.number_input("Número inicial de folio:", min_value=0, value=1, step=1)
with col_num2:
    text_color = st.color_picker("Color del número:", "#FF0000") # Rojo por defecto para que resalte

# 2. Carga de archivos
uploaded_files = st.file_uploader("Sube tus archivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    files_dict = {f.name: f for f in uploaded_files}
    filenames = list(files_dict.keys())

    st.subheader("↕️ Ordenar para foliar")
    sorted_filenames = sort_items(filenames, direction="vertical", key="sort_pdf")

    if st.button("🚀 UNIR Y ENUMERAR PÁGINAS"):
        with st.spinner("Procesando folios..."):
            try:
                writer = PdfWriter()
                current_page_number = start_number

                for name in sorted_filenames:
                    reader = PdfReader(files_dict[name])
                    
                    for page in reader.pages:
                        # Crear un PDF temporal en memoria para el número
                        packet = io.BytesIO()
                        can = canvas.Canvas(packet, pagesize=(page.mediabox.width, page.mediabox.height))
                        
                        # Configurar fuente y color
                        can.setFont("Helvetica-Bold", 12)
                        can.setFillColor(text_color)
                        
                        # Dibujar el número (Esquina inferior derecha)
                        # Ajustamos un poco los márgenes (30 puntos desde los bordes)
                        can.drawRightString(float(page.mediabox.width) - 30, 30, f"{current_page_number}")
                        can.save()
                        
                        # Mover el "puntero" al inicio del stream
                        packet.seek(0)
                        new_pdf = PdfReader(packet)
                        
                        # Combinar la página original con la del número
                        page.merge_page(new_pdf.pages[0])
                        writer.add_page(page)
                        
                        current_page_number += 1
                
                # Guardar el PDF final
                output = io.BytesIO()
                writer.write(output)
                writer.close()
                
                st.success(f"¡Listo! Se enumeraron las páginas desde la {start_number} hasta la {current_page_number - 1}")
                
                st.download_button(
                    label="💾 Descargar PDF Foliado",
                    data=output.getvalue(),
                    file_name=f"ANEXO_FOLIADO_{start_number}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error técnico: {e}")

else:
    st.info("Sube los documentos para habilitar el foliador automático.")

st.divider()
st.caption("Nota: El número se coloca automáticamente en la esquina inferior derecha de cada página.")
