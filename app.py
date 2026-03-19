import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
from streamlit_sortables import sort_items
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from streamlit_js_eval import streamlit_js_eval

# Configuración de página
st.set_page_config(page_title="Unidor Pro - Memoria de Calibración", layout="wide", page_icon="🔢")

# Estética Minimalista Oscura
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .stButton>button { border-radius: 6px; background-color: #238636; color: white; border: 1px solid rgba(240,246,252,0.1); font-weight: 600;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE MEMORIA DEL NAVEGADOR ---
def save_setting(key, value):
    streamlit_js_eval(js_expressions=f"localStorage.setItem('{key}', '{value}')", want_output=False)

def load_setting(key, default):
    val = streamlit_js_eval(js_expressions=f"localStorage.getItem('{key}')", key=key)
    return val if val is not None else default

# Cargamos los valores guardados (o los de defecto si es la primera vez)
saved_x = load_setting('pdf_x', "17.0")
saved_y = load_setting('pdf_y', "1.5")
saved_size = load_setting('pdf_size', "12")
saved_prefix = load_setting('pdf_prefix', "")

# --- PANEL DE CONTROL (SIDEBAR) ---
st.sidebar.title("⚙️ Ajustes Guardados")
activar_folio = st.sidebar.checkbox("🔢 Activar Foliado", value=True)

if activar_folio:
    st.sidebar.subheader("📍 Calibración (cm)")
    
    # Sliders con memoria
    pos_x_cm = st.sidebar.slider("Desde la IZQUIERDA", 0.0, 21.0, float(saved_x), step=0.1, key="slider_x")
    pos_y_top_cm = st.sidebar.slider("Desde ARRIBA", 0.0, 28.0, float(saved_y), step=0.1, key="slider_y")
    font_size = st.sidebar.slider("Tamaño de Letra", 6, 36, int(saved_size), key="slider_size")
    text_prefix = st.sidebar.text_input("Prefijo (ej: Folio:)", value=saved_prefix, key="input_prefix")

    # Botón para fijar la posición
    if st.sidebar.button("💾 GUARDAR POSICIÓN ACTUAL"):
        save_setting('pdf_x', pos_x_cm)
        save_setting('pdf_y', pos_y_top_cm)
        save_setting('pdf_size', font_size)
        save_setting('pdf_prefix', text_prefix)
        st.sidebar.success("✅ ¡Posición fijada en este navegador!")

    st.sidebar.divider()
    start_number = st.sidebar.number_input("Empezar en el número:", min_value=0, value=1)
    text_color = st.sidebar.color_picker("Color del número", "#FF0000")

if st.sidebar.button("🗑️ Limpiar Archivos"):
    st.session_state.clear()
    st.rerun()

# --- CUERPO PRINCIPAL ---
st.title("📄 Unidor y Foliador de Precisión")
st.write("Sube tus documentos. El orden y la numeración se procesan en la RAM.")

uploaded_files = st.file_uploader("Cargar PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    files_dict = {f.name: f for f in uploaded_files}
    filenames = list(files_dict.keys())

    st.subheader("↕️ Orden de los archivos")
    sorted_filenames = sort_items(filenames, direction="vertical", key="sort_list")

    if st.button("🚀 PROCESAR Y DESCARGAR"):
        with st.spinner("Generando documento..."):
            try:
                writer = PdfWriter()
                current_num = start_number
                
                for name in sorted_filenames:
                    reader = PdfReader(files_dict[name])
                    for page in reader.pages:
                        if activar_folio:
                            packet = io.BytesIO()
                            w_pts = float(page.mediabox.width)
                            h_pts = float(page.mediabox.height)
                            
                            can = canvas.Canvas(packet, pagesize=(w_pts, h_pts))
                            can.setFont("Helvetica-Bold", font_size)
                            can.setFillColor(text_color)
                            
                            # Cálculo: CM a Puntos (1cm = 28.346 pts)
                            x_final = pos_x_cm * 28.346
                            y_final = h_pts - (pos_y_top_cm * 28.346)
                            
                            can.drawString(x_final, y_final, f"{text_prefix}{current_num}")
                            can.save()
                            packet.seek(0)
                            page.merge_page(PdfReader(packet).pages[0])
                        
                        writer.add_page(page)
                        current_num += 1

                output = io.BytesIO()
                writer.write(output)
                writer.close()
                st.success("¡PDF Generado!")
                st.download_button("📥 Guardar PDF Final", data=output.getvalue(), file_name="Documento_Finalizado.pdf")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("Esperando archivos para procesar...")
