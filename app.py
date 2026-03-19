import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
from streamlit_sortables import sort_items
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm 

# Configuración de página
st.set_page_config(page_title="Unidor de PDFs Profesional", layout="wide", page_icon="📄")

# Estética Minimalista Oscura (Cero distracciones)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .stButton>button { border-radius: 6px; background-color: #238636; color: white; border: 1px solid rgba(240,246,252,0.1); font-weight: 600;}
    .stButton>button:hover { background-color: #2ea043; }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL DE CONTROL (SIDEBAR) ---
st.sidebar.title("⚙️ Opciones de Salida")

# INTERRUPTOR PRINCIPAL: ¿Quiere numerar o solo unir?
activar_folio = st.sidebar.checkbox("🔢 Activar Foliado (Numeración)", value=False)

if activar_folio:
    st.sidebar.subheader("📍 Configuración del Folio")
    start_number = st.sidebar.number_input("Número Inicial", min_value=0, value=1)
    text_prefix = st.sidebar.text_input("Prefijo (ej: Folio:)", value="")
    font_size = st.sidebar.slider("Tamaño de Fuente", 6, 36, 12)
    text_color = st.sidebar.color_picker("Color del Texto", "#FF0000")
    
    st.sidebar.write("**Posición Exacta (cm)**")
    pos_x_cm = st.sidebar.slider("Desde la IZQUIERDA", 0.0, 21.0, 17.0, step=0.1)
    pos_y_top_cm = st.sidebar.slider("Desde ARRIBA", 0.0, 28.0, 1.5, step=0.1)
else:
    st.sidebar.info("Modo actual: **Solo Combinar**. Los archivos se unirán sin marcas adicionales.")

if st.sidebar.button("🧹 Limpiar Todo"):
    st.session_state.clear()
    st.rerun()

# --- ÁREA DE TRABAJO ---
st.title("📄 Unidor de PDFs Contable")
st.write("Sube tus archivos, ordénalos y genera un solo documento final.")

uploaded_files = st.file_uploader("Cargar archivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    files_dict = {f.name: f for f in uploaded_files}
    filenames = list(files_dict.keys())

    st.subheader("↕️ Orden de los documentos")
    st.caption("Arrastra para definir el orden de unión:")
    sorted_filenames = sort_items(filenames, direction="vertical", key="sort_main")

    st.divider()

    if st.button("🚀 PROCESAR Y DESCARGAR"):
        with st.spinner("Generando documento..."):
            try:
                writer = PdfWriter()
                
                if activar_folio:
                    # LÓGICA CON FOLIADO (Procesa página por página)
                    current_page_number = start_number
                    for name in sorted_filenames:
                        reader = PdfReader(files_dict[name])
                        for page in reader.pages:
                            packet = io.BytesIO()
                            w_pts = float(page.mediabox.width)
                            h_pts = float(page.mediabox.height)
                            
                            can = canvas.Canvas(packet, pagesize=(w_pts, h_pts))
                            can.setFont("Helvetica-Bold", font_size)
                            can.setFillColor(text_color)
                            
                            x_final = pos_x_cm * 28.346
                            y_final = h_pts - (pos_y_top_cm * 28.346)
                            
                            text_to_print = f"{text_prefix}{current_page_number}"
                            can.drawString(x_final, y_final, text_to_print)
                            can.save()
                            
                            packet.seek(0)
                            num_pdf = PdfReader(packet)
                            page.merge_page(num_pdf.pages[0])
                            writer.add_page(page)
                            current_page_number += 1
                else:
                    # LÓGICA SIMPLE (Solo combina, es mucho más rápido)
                    for name in sorted_filenames:
                        reader = PdfReader(files_dict[name])
                        for page in reader.pages:
                            writer.add_page(page)

                # Resultado
                output = io.BytesIO()
                writer.write(output)
                writer.close()
                
                st.success("¡Documento listo para descargar!")
                nombre_archivo = "Unido_Foliado.pdf" if activar_folio else "Documento_Unido.pdf"
                st.download_button("📥 Descargar PDF Final", data=output.getvalue(), file_name=nombre_archivo, mime="application/pdf")
                
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.warning("Sube los archivos para comenzar.")

st.divider()
st.caption("Procesamiento efímero en RAM. No se guardan datos en el servidor.")
