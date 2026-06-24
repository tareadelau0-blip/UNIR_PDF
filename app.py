import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
import json
import os
from streamlit_sortables import sort_items
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Unidor Pro - Configuración Completa", layout="wide")

# --- GESTIÓN DE CONFIGURACIÓN JSON ---
CONFIG_FILE = 'config.json'

def load_all_configs():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    # Perfil por defecto
    return {"General": {"pos_x": 17.0, "pos_y": 1.5, "font_size": 12, "prefix": "", "color": "#FF0000"}}

def save_all_configs(configs):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(configs, f, indent=4)

if 'configs' not in st.session_state:
    st.session_state.configs = load_all_configs()

# --- SIDEBAR (CONTROLES) ---
st.sidebar.title("⚙️ Memoria de Foliado")

# Selector de Perfil
perfil_actual = st.sidebar.selectbox("Seleccionar Perfil", list(st.session_state.configs.keys()))
conf = st.session_state.configs[perfil_actual]

# Gestión de perfiles
nuevo_perfil = st.sidebar.text_input("Nombre para nuevo perfil")
if st.sidebar.button("➕ Crear nuevo perfil"):
    if nuevo_perfil and nuevo_perfil not in st.session_state.configs:
        st.session_state.configs[nuevo_perfil] = conf.copy()
        save_all_configs(st.session_state.configs)
        st.rerun()

# Controles de edición
activar_folio = st.sidebar.checkbox("🔢 Activar Foliado", value=True)

if activar_folio:
    st.sidebar.subheader(f"📍 Editando: {perfil_actual}")
    
    pos_x = st.sidebar.slider("X (cm desde izq.)", 0.0, 30.0, float(conf.get('pos_x', 17.0)), step=0.1)
    pos_y = st.sidebar.slider("Y (cm desde arriba)", 0.0, 28.0, float(conf.get('pos_y', 1.5)), step=0.1)
    f_size = st.sidebar.slider("Tamaño Fuente", 6, 36, int(conf.get('font_size', 12)))
    prefix = st.sidebar.text_input("Prefijo", value=conf.get('prefix', ""))
    color_elegido = st.sidebar.color_picker("Color del Folio", value=conf.get('color', "#FF0000"))

    if st.sidebar.button("💾 Guardar cambios en perfil"):
        st.session_state.configs[perfil_actual] = {
            "pos_x": round(pos_x, 2),
            "pos_y": round(pos_y, 2),
            "font_size": f_size,
            "prefix": prefix,
            "color": color_elegido
        }
        save_all_configs(st.session_state.configs)
        st.sidebar.success("✅ Configuración guardada")

    if st.sidebar.button("🗑️ Borrar perfil actual"):
        if len(st.session_state.configs) > 1:
            del st.session_state.configs[perfil_actual]
            save_all_configs(st.session_state.configs)
            st.rerun()
        else:
            st.sidebar.error("No puedes borrar el único perfil.")

# Botón oculto avanzado
with st.sidebar.expander("🛠️ Avanzado"):
    if st.button("🧹 Clear Database"):
        st.session_state.configs = {"General": {"pos_x": 17.0, "pos_y": 1.5, "font_size": 12, "prefix": "", "color": "#FF0000"}}
        save_all_configs(st.session_state.configs)
        st.rerun()

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
                        
                        can.setFont("Helvetica-Bold", conf['font_size'])
                        can.setFillColor(conf['color'])
                        
                        # Cálculo de posición usando el perfil seleccionado
                        can.drawString(conf['pos_x'] * 28.346, h - (conf['pos_y'] * 28.346), f"{conf['prefix']}{curr_num}")
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
