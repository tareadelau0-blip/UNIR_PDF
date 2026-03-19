import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
import json
import os
from streamlit_sortables import sort_items
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

st.set_page_config(page_title="Unidor Pro - Configuración JSON", layout="wide")

# --- FUNCIÓN PARA MANEJAR EL JSON ---
CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"pos_x": 17.0, "pos_y": 1.5, "font_size": 12, "prefix": ""}

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

# Cargar configuración al iniciar
if 'config' not in st.session_state:
    st.session_state.config = load_config()

# --- SIDEBAR ---
st.sidebar.title("⚙️ Parámetros del JSON")
activar_folio = st.sidebar.checkbox("🔢 Activar Foliado", value=True)

if activar_folio:
    # Usamos los valores cargados del JSON
    pos_x = st.sidebar.slider("X (cm)", 0.0, 21.0, float(st.session_state.config['pos_x']), step=0.1)
    pos_y = st.sidebar.slider("Y Superior (cm)", 0.0, 28.0, float(st.session_state.config['pos_y']), step=0.1)
    f_size = st.sidebar.slider("Tamaño Fuente", 6, 36, int(st.session_state.config['font_size']))
    prefix = st.sidebar.text_input("Prefijo", value=st.session_state.config['prefix'])

    if st.sidebar.button("💾 SOBRESCRIBIR CONFIGURACIÓN"):
        nueva_conf = {
            "pos_x": pos_x,
            "pos_y": pos_y,
            "font_size": f_size,
            "prefix": prefix
        }
        save_config(nueva_conf)
        st.session_state.config = nueva_conf
        st.sidebar.success("Configuración guardada en JSON local.")

# --- CUERPO PRINCIPAL ---
st.title("📄 Unidor de PDFs con Memoria JSON")
uploaded_files = st.file_uploader("Cargar archivos", type="pdf", accept_multiple_files=True)

if uploaded_files:
    files_dict = {f.name: f for f in uploaded_files}
    sorted_names = sort_items(list(files_dict.keys()), direction="vertical", key="sorter")

    start_num = st.number_input("Número Inicial", value=1)

    if st.button("🚀 PROCESAR"):
        writer = PdfWriter()
        curr_num = start_num
        for name in sorted_names:
            reader = PdfReader(files_dict[name])
            for page in reader.pages:
                if activar_folio:
                    packet = io.BytesIO()
                    w, h = float(page.mediabox.width), float(page.mediabox.height)
                    can = canvas.Canvas(packet, pagesize=(w, h))
                    can.setFont("Helvetica-Bold", f_size)
                    can.setFillColor("#FF0000") # Rojo contable
                    can.drawString(pos_x * 28.346, h - (pos_y * 28.346), f"{prefix}{curr_num}")
                    can.save()
                    packet.seek(0)
                    page.merge_page(PdfReader(packet).pages[0])
                writer.add_page(page)
                curr_num += 1
        
        output = io.BytesIO()
        writer.write(output)
        st.download_button("📥 Descargar", data=output.getvalue(), file_name="unido_final.pdf")
