import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
from streamlit_sortables import sort_items
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm  # Para medidas reales

st.set_page_config(page_title="Foliador de Precisión Contable", layout="wide", page_icon="🔢")

# Estética Profesional Minimalista Oscura
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #f0f0f0; }
    [data-testid="stSidebar"] { background-color: #1e1e1e; border-right: 1px solid #333; }
    .stButton>button { border-radius: 5px; background-color: #007bff; color: white; border: none; font-weight: bold;}
    .stButton>button:hover { background-color: #0056b3; }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL DE CONTROL TÉCNICO (SIDEBAR) ---
st.sidebar.title("📏 Calibración del Folio")
st.sidebar.write("Ajusta las medidas para que coincidan con tu formulario.")

st.sidebar.subheader("1️⃣ Texto y Número")
start_number = st.sidebar.number_input("Número Inicial", min_value=0, value=1)
# NUEVO: Campo para prefijo (ej: "Folio:", "Pág.", o vacío)
text_prefix = st.sidebar.text_input("Texto antes del número (Opcional)", value="Folio: ", help="Ej: 'Folio: ', 'Pág. ', o déjalo vacío si el papel ya lo trae.")

st.sidebar.divider()

st.sidebar.subheader("2️⃣ Estilo y Color")
font_size = st.sidebar.slider("Tamaño de Fuente (pts)", 6, 36, 12)
text_color = st.sidebar.color_picker("Color del Texto", "#FF0000")

st.sidebar.divider()

st.sidebar.subheader("3️⃣ Posición Exacta (en cm)")
st.sidebar.caption("Medido desde las esquinas del papel. Precisión de 1mm.")

# Cambiamos la lógica: Ahora medimos desde la IZQUIERDA para alineación fácil
pos_x_cm = st.sidebar.slider("Distancia desde el borde IZQUIERDO (cm)", 0.5, 20.0, 15.0, step=0.1)
pos_y_cm = st.sidebar.slider("Distancia desde el borde INFERIOR (cm)", 0.5, 25.0, 2.0, step=0.1)

if st.sidebar.button("🧹 Limpiar Memoria"):
    st.session_state.clear()
    st.rerun()

# --- ÁREA DE TRABAJO ---
st.title("📄 Unidor y Foliador de Alta Precisión")
st.info("Configura la posición y el texto en el panel izquierdo. Esta herramienta es efímera y procesa todo en la RAM.")

uploaded_files = st.file_uploader("Cargar archivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    files_dict = {f.name: f for f in uploaded_files}
    filenames = list(files_dict.keys())

    st.subheader("↕️ Orden de Foliado")
    st.caption("Arrastra los nombres para definir el orden correlativo:")
    sorted_filenames = sort_items(filenames, direction="vertical", key="sort_contable")

    if st.button("🚀 GENERAR PDF FOLIADO CON PRECISIÓN"):
        with st.spinner("Estampando números de página..."):
            try:
                writer = PdfWriter()
                current_page_number = start_number

                for name in sorted_filenames:
                    reader = PdfReader(files_dict[name])
                    
                    for page in reader.pages:
                        # Crear capa de texto en memoria
                        packet = io.BytesIO()
                        # Dimensiones reales de la página actual
                        w_pts = float(page.mediabox.width)
                        h_pts = float(page.mediabox.height)
                        
                        can = canvas.Canvas(packet, pagesize=(w_pts, h_pts))
                        can.setFont("Helvetica-Bold", font_size)
                        can.setFillColor(text_color)
                        
                        # CONVERSIÓN DE CM A PUNTOS POSTSCRIPT (1 cm = 28.346 pts)
                        x_final = pos_x_cm * 28.346
                        y_final = pos_y_cm * 28.346
                        
                        # CREAR EL TEXTO FINAL
                        text_to_print = f"{text_prefix}{current_page_number}"
                        
                        # DIBUJAR: Usamos drawString (Alineación Izquierda) por defecto
                        # Esto asegura que el texto empiece EXACTAMENTE en la coordenada X elegida.
                        can.drawString(x_final, y_final, text_to_print)
                        can.save()
                        
                        packet.seek(0)
                        num_pdf = PdfReader(packet)
                        
                        # Combinar capas
                        page.merge_page(num_pdf.pages[0])
                        writer.add_page(page)
                        
                        current_page_number += 1
                
                # Resultado final
                output = io.BytesIO()
                writer.write(output)
                writer.close()
                
                st.success(f"¡Listo! Se foliaron {current_page_number - start_number} páginas con precisión milimétrica.")
                st.download_button(
                    label="📥 Descargar Documento Calibrado",
                    data=output.getvalue(),
                    file_name=f"Foliado_{text_prefix.strip()}_{start_number}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error técnico: {e}")
else:
    st.warning("Por favor, sube los archivos para comenzar.")

st.divider()
st.caption("Herramienta de nivel profesional para uso contable. No almacena datos personales.")
