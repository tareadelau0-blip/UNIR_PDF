import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
import json
import os
from streamlit_sortables import sort_items
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

st.set_page_config(page_title="Unidor Pro - Configuración Completa", layout="wide")

# --- GESTIÓN DE CONFIGURACIÓN JSON ---
CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    # Valores por defecto si el archivo falla o no existe
    return {"pos_x": 17.0, "pos_y": 1.5, "font_size": 12, "prefix": "", "color": "#FF0000"}

def save_config(config_data):
    # Nota: En Streamlit Cloud esto solo dura mientras la sesión esté activa 
    # debido a permisos de escritura en GitHub.
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

# Cargar configuración en el estado de la sesión
if 'config' not in st.session_state:
    st.session_state.config = load_config()

# --- SIDEBAR (CONTROLES) ---
st.sidebar.title("⚙️ Memoria de Foliado")
activar_folio = st.sidebar.checkbox("🔢 Activar Foliado", value=True)

if activar_folio:
    st.sidebar.subheader("📍 Posición y Estilo")
    
    # Sliders cargando valores del JSON
    pos_x = st.sidebar.slider("X (cm desde izq.)", 0.0, 21.0, float(st.session_state.config.get('pos_x', 17.0)), step=0.1)
    pos_y = st.sidebar.slider("Y (cm desde arriba)", 0.0, 28.0, float(st.session_state.config.get('pos_y', 1.5)), step=0.1)
    f_size = st.sidebar.slider("Tamaño Fuente", 6, 36, int(st.session_state.config.get('font_size', 12)))
    prefix = st.sidebar.text_input("Prefijo", value=st.session_state.config.get('prefix', ""))
    
    # NUEVO: Selector de color vinculado al JSON
    color_elegido = st.sidebar.color_picker("Color del Folio", value=st.session_state.config.get('color', "#FF0000"))

    if st.sidebar.button("💾 GUARDAR COMO PREDETERMINADO"):
        nueva_conf = {
            "pos_x": pos_x,
            "pos_y": pos_y,
            "font_size": f_size,
            "prefix": prefix,
            "color": color_elegido
        }
        save_config(nueva_conf)
        st.session_state.config = nueva_conf
        st.sidebar.success("✅ Configuración actualizada")

# --- CUERPO PRINCIPAL ---
st.title("📄 Unidor de PDFs Contable")

uploaded_files = st.file_uploader("Subir archivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    files_dict = {f.name: f for f in uploaded_files}
    sorted_names = sort_items(list(files_dict.keys()), direction="vertical", key="unidor_sort")

    st.divider()
    start_num = st.number_input("Número de folio inicial", value=1, step=1)

    if st.button("🚀 PROCESAR Y DESCARGAR"):
        writer = PdfWriter()
        curr_num = start_num
        
        try:
            for name in sorted_names:
                reader = PdfReader(files_dict[name])
                for page in reader.pages:
                    if activar_folio:
                        packet = io.BytesIO()
                        w, h = float(page.mediabox.width), float(page.mediabox.height)
                        can = canvas.Canvas(packet, pagesize=(w, h))
                        
                        # USAR EL COLOR DEL JSON/SELECTOR
                        can.setFont("Helvetica-Bold", f_size)
                        can.setFillColor(color_elegido)
                        
                        # Cálculo de posición
                        can.drawString(pos_x * 28.346, h - (pos_y * 28.346), f"{prefix}{curr_num}")
                        can.save()
                        
                        packet.seek(0)
                        page.merge_page(PdfReader(packet).pages[0])
                    
                    writer.add_page(page)
                    curr_num += 1
            
            output = io.BytesIO()
            writer.write(output)
            st.success("¡PDF generado exitosamente!")
            st.download_button("📥 Descargar Resultado", data=output.getvalue(), file_name="resultado_unido.pdf", mime="application/pdf")
            
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
