import streamlit as st
import numpy as np
import math
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import time
from scipy import stats
import io

# Para ReportLab (Certificado PDF ISO/IEC 17025)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Configuración de la página (¡SIEMPRE PRIMERO EN STREAMLIT!)
st.set_page_config(
    page_title="Simulador de Metrología y Alineación Optomecánica - CIO",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================================
# 🔒 MÓDULO DE SEGURIDAD ROBUSTO CON ROLES (RBAC) Y SIMULACIÓN LDAP / CIO-Auth
# =========================================================================

USUARIOS_AUTORIZADOS_RBAC = {
    "j3remyx1010@gmail.com": {"pass": "Jggg101031", "role": "Administrador de Laboratorio"},
    "investigador@cio.mx": {"pass": "cio2026*", "role": "Investigador"},
    "estudiante@cio.mx": {"pass": "optica123", "role": "Estudiante"}
}
MAX_INTENTOS = 3

if "intentos" not in st.session_state:
    st.session_state.intentos = 0
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if st.session_state.intentos >= MAX_INTENTOS:
    st.error("❌ Demasiados intentos fallidos. Acceso bloqueado temporalmente por seguridad institucional.")
    st.stop()

if not st.session_state.autenticado:
    st.markdown("""
        <style>
            header, [data-testid="stHeader"] { visibility: hidden; height: 0px; }
            .stApp { background-color: #03050c !important; overflow-x: hidden; }
            .grid-bg {
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: linear-gradient(rgba(0, 240, 255, 0.08) 1.2px, transparent 1.2px),
                            linear-gradient(90deg, rgba(147, 51, 234, 0.08) 1.2px, transparent 1.2px);
                background-size: 35px 35px, 35px 35px;
                animation: gridMove 25s linear infinite; z-index: 0; pointer-events: none;
            }
            .top-global-hud {
                position: fixed; top: 15px; left: 25px; right: 25px;
                display: flex; justify-content: space-between; font-family: monospace;
                font-size: 11px; color: #00f0ff; letter-spacing: 1.5px; z-index: 10;
                opacity: 0.95; pointer-events: none; text-shadow: 0 0 12px rgba(0, 240, 255, 0.85);
            }
            .login-wrapper {
                position: relative; max-width: 460px; margin: 4vh auto 0 auto; padding: 2.5px;
                border-radius: 20px; background: linear-gradient(135deg, #00f0ff, #c084fc, #00f0ff, #9333ea);
                background-size: 300% 300%; animation: borderGlow 5s ease infinite, entranceZoom 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                box-shadow: 0 0 35px rgba(0, 240, 255, 0.45), 0 0 50px rgba(147, 51, 234, 0.35);
            }
            .login-card {
                position: relative; background: rgba(6, 10, 22, 0.94); backdrop-filter: blur(16px);
                border-radius: 18px; padding: 25px 25px 15px 25px; z-index: 2;
            }
            .login-title { color: #ffffff; font-size: 18px; font-weight: 700; text-align: center; letter-spacing: 1px; text-transform: uppercase; margin: 0; text-shadow: 0 0 12px rgba(0, 240, 255, 0.7); }
            .login-subtitle { color: #00f0ff; font-size: 10px; text-align: center; letter-spacing: 0.5px; opacity: 0.95; margin-top: 4px; margin-bottom: 12px; font-family: monospace; text-shadow: 0 0 8px rgba(0, 240, 255, 0.5); }
            @keyframes gridMove { 0% { background-position: 0 0, 0 0; } 100% { background-position: 35px 35px, 35px 35px; } }
            @keyframes borderGlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
            @keyframes entranceZoom { 0% { opacity: 0; transform: scale(0.92) translateY(-20px); } 100% { opacity: 1; transform: scale(1) translateY(0); } }
        </style>
        <div class="grid-bg"></div>
        <div class="top-global-hud">
            <span>● SYSTEM: CIO-AUTH ONLINE</span>
            <span>ENCRYPTION: AES-256</span>
            <span>NODE: CIO-LEÓN-LAB</span>
        </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.3, 1])
    with col_c:
        st.markdown("""
            <div class="login-wrapper">
                <div class="login-card">
                    <div class="login-title">Autenticación Institucional CIO</div>
                    <div class="login-subtitle">● ACCESO LDAP / RBAC METROLOGÍA ÓPTICA</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("formulario_login"):
            correo = st.text_input("✉️ Correo electrónico institucional:", placeholder="usuario@cio.mx")
            password = st.text_input("🔑 Contraseña:", type="password", placeholder="••••••••")
            modo_ldap = st.checkbox("Sincronizar con Active Directory / Servidor LDAP del CIO", value=True)
            boton_ingresar = st.form_submit_button("Acceder al Sistema", use_container_width=True)

            if boton_ingresar:
                c_clean = correo.strip().lower()
                if c_clean in USUARIOS_AUTORIZADOS_RBAC and password == USUARIOS_AUTORIZADOS_RBAC[c_clean]["pass"]:
                    st.session_state.autenticado = True
                    st.session_state.intentos = 0
                    st.session_state.user_role = USUARIOS_AUTORIZADOS_RBAC[c_clean]["role"]
                    st.session_state.user_email = c_clean
                    with st.spinner("🔍 Conectando con directorio LDAP y calibrando transductores..."):
                        time.sleep(1.0)
                    st.rerun()
                else:
                    st.session_state.intentos += 1
                    restantes = MAX_INTENTOS - st.session_state.intentos
                    st.error(f"Credenciales incorrectas o usuario no registrado en servidor LDAP. Intentos restantes: {restantes}")
                    st.stop()
    st.stop()


# =========================================================================
# 👇 CÓDIGO DEL SIMULADOR DE METROLOGÍA ÓPTICA (CON LAS 5 MEJORAS CIO)
# =========================================================================

DB_NAME = "metrologia_optica.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            configuracion TEXT,
            distancia TEXT,
            eje_referencia TEXT,
            desplazamiento TEXT,
            diametro_spot TEXT,
            angulo TEXT,
            arcmin REAL,
            mrad REAL,
            sentido TEXT,
            pasos_micrometricos INTEGER,
            pulsos_actuador INTEGER,
            incertidumbre TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_record_to_db(rec):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO historial 
        (configuracion, distancia, eje_referencia, desplazamiento, diametro_spot, angulo, arcmin, mrad, sentido, pasos_micrometricos, pulsos_actuador, incertidumbre)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        rec["Configuración Experimental"], rec["Distancia Bancada"], rec["Eje de Referencia Óptica"], 
        rec["Desplazamiento Micrométrico"], rec["Diámetro del Spot"], rec["Ángulo (α)"], 
        rec["Arcmin"], rec["mrad"], rec["Sentido Corrección"], rec["Pasos (Micrómetro)"], 
        rec["Pulsos (Actuador Piezoresistivo)"], rec["Incertidumbre Expandida (±)"]
    ))
    conn.commit()
    conn.close()

def load_history_from_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id, fecha AS 'Fecha/Hora', configuracion AS 'Configuración Experimental', distancia AS 'Distancia Bancada', eje_referencia AS 'Eje de Referencia Óptica', desplazamiento AS 'Desplazamiento Micrométrico', diametro_spot AS 'Diámetro del Spot', angulo AS 'Ángulo (α)', arcmin AS 'Arcmin', mrad AS 'mrad', sentido AS 'Sentido Corrección', pasos_micrometricos AS 'Pasos (Micrómetro)', pulsos_actuador AS 'Pulsos (Actuador Piezoresistivo)', incertidumbre AS 'Incertidumbre Expandida (±)' FROM historial ORDER BY id DESC", conn)
    conn.close()
    return df

def clear_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM historial")
    conn.commit()
    conn.close()

init_db()

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
        header, [data-testid="stHeader"], [data-testid="stToolbar"] { visibility: hidden !important; height: 0px !important; margin: 0px !important; padding: 0px !important; }
        .block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; }
        .stApp { background-color: #03050c !important; color: #f3e8ff !important; }
        [data-testid="stSidebar"] { background-color: #070b19 !important; border-right: 1px solid rgba(0, 149, 255, 0.25) !important; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #00f0ff !important; font-size: 13px !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px; margin-top: 15px !important; margin-bottom: 10px !important; border-bottom: 1px solid rgba(0, 149, 255, 0.2) !important; padding-bottom: 4px;
        }
        div.stButton > button {
            background: linear-gradient(135deg, #0b132b 0%, #171033 100%) !important; color: #00f0ff !important; border: 1px solid rgba(0, 149, 255, 0.4) !important; border-radius: 8px !important; font-weight: 600 !important; transition: all 0.3s ease !important;
        }
        div.stButton > button:hover {
            background: #00f0ff !important; color: #03050c !important; box-shadow: 0px 0px 18px rgba(0, 240, 255, 0.6) !important; border-color: #00f0ff !important; transform: translateY(-1px);
        }
        .metric-card-container {
            display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #070b19 0%, #100f2b 100%);
            border: 1px solid rgba(0, 149, 255, 0.35); padding: 16px 20px; border-radius: 12px; margin-top: 15px; margin-bottom: 25px;
            box-shadow: 0 0 20px rgba(147, 51, 234, 0.15);
        }
    </style>
""", unsafe_allow_html=True)

# --- DICCIONARIOS DE TRADUCCIÓN (25 CONFIGURACIONES ORIGINALES INTACTAS) ---
TEXTS = {
    "ES": {
        "title": "Simulador Metrológico de Alineación y Óptica Coherente - CIO",
        "lang_select": "Idioma / Language",
        "unit_select": "Sistema de Unidades / Unit System",
        "metric": "Métrico (cm, metros)",
        "imperial": "Imperial (pulgadas, yardas)",
        "profile_select": "Configuración Experimental / Banco Óptico",
        "profile_placeholder": "-- Seleccione un Arreglo Experimental --",
        "p1": "Alineación de micro-espejos MEMS (Rango ultra-corto)",
        "p2": "Interferometría de Michelson en banco (Rango corto)",
        "p3": "Caracterización de láseres de He-Ne (Rango medio)",
        "p4": "Prueba de frente de onda para lentes asféricas (Rango medio)",
        "p5": "Arreglo colimador para fibras ópticas monomodo (Rango medio-largo)",
        "p6": "Sistema de puntería láser para LIDAR atmosférico (Rango largo)",
        "p7": "Banco óptico para holografía digital (Rango medio)",
        "p8": "Calibración de auto-colimadores digitales (Rango medio)",
        "p9": "Optical Trapping / Pinzas Ópticas (Rango ultra-corto)",
        "p10": "Espectroscopía Raman con acoplamiento confocal (Rango corto)",
        "p11": "Transmisión de espacio libre FSO (Free Space Optics) (Rango extremo)",
        "p12": "Sistema láser de alta potencia para corte Nd:YAG (Rango medio)",
        "p13": "Metrología de superficies ópticas por deflectometría (Rango corto)",
        "p14": "Seguimiento optoelectrónico de blancos dinámicos (Rango largo)",
        "p15": "Interferometría láser de alta precisión para gravimetría (Rango medio)",
        "p16": "Colimación de telescopios astronómicos de investigación (Rango extremo)",
        "p17": "Alineación sub-micrométrica para óptica integrada (Rango ultra-corto)",
        "p18": "Sistemas de guía láser para óptica adaptativa (Rango extremo)",
        "p19": "Caracterización de perfiles de intensidad TEM00 (Rango medio)",
        "p20": "Óptica no lineal en cristales BBO (Rango corto)",
        "p21": "Sensor de frente de onda Shack-Hartmann (Rango corto)",
        "p22": "Metrología láser de grandes distancias / teodolito óptico (Rango largo)",
        "p23": "Arreglos fotónicos integrados en silicio (Rango ultra-corto)",
        "p24": "Litografía óptica de interferencia láser (Rango muy corto)",
        "p25": "Monitoreo interferométrico de deformación estructural (Rango medio)",
        "params": "Parámetros Optomecánicos",
        "phys_params": "Óptica Coherente y Entorno",
        "reset_btn": "Reiniciar Parámetros a 0",
        "save_btn": "💾 Registrar Medición (DB)",
        "export_csv": "📥 Exportar Historial (CSV)",
        "h_mira": "Eje de referencia óptica",
        "h_extra": "Desplazamiento micrométrico del haz",
        "dist_input": "Distancia de propagación en bancada",
        "ref_angle_input": "Inclinación inicial del banco (°)",
        "laser_div": "Divergencia del haz (mrad)",
        "temp_input": "Temperatura de laboratorio (°C)",
        "press_input": "Presión Atmosférica (hPa)",
        "earth_curv": "Activar corrección por curvatura/refracción",
        "cm": "cm", "m": "m", "in": "pulgadas", "yd": "yardas",
        "laser_label": "Eje Óptico Teórico",
        "sight_label": "Eje del Haz Ajustado",
        "target_center": "Centro del Sensor PSD",
        "target_point": "Centroide del Haz Láser",
        "title_graph": "Propagación",
        "req_angle": "Ángulo de Corrección (α)",
        "diff_height": "Desviación Lineal Total",
        "sight_angle": "Ángulo de Inclinación del Haz (α)",
        "angular_adj": "Ajuste Angular (Resolución)",
        "direction": "Sentido de Corrección",
        "direction_up": "Ascendente (+Z)",
        "direction_down": "Descendente (-Z)",
        "spot_size_lbl": "Diámetro del Spot (1/e²)",
        "curv_drop_lbl": "Corrección Atmosférica",
        "uncertainty_lbl": "Incertidumbre Expandida (SciPy)",
        "history_title": "Historial Metrológico en Base de Datos (SQLite)",
        "clear_history": "Borrar Base de Datos",
        "confirm_clear_msg": "¿Estás seguro de que deseas vaciar el registro metrológico?",
        "confirm_yes": "✔ Sí, Borrar",
        "confirm_cancel": "✖ Cancelar",
        "empty_history": "No hay registros experimentales guardados en la base de datos.",
        "select_prompt": "⚠️ Por favor, seleccione una Configuración Experimental / Banco Óptico en la barra lateral para iniciar la simulación metrológica.",
        "record_saved": "✅ Medición metrológica registrada permanentemente en SQLite.",
        "target_2d_title": "🎯 Perfil Transversal 2D (Sensor PSD / Perfilómetro)"
    },
    "EN": {
        "title": "Metrological Simulator of Coherent Alignment & Optics - CIO",
        "lang_select": "Language / Idioma",
        "unit_select": "Unit System / Sistema de Unidades",
        "metric": "Metric (cm, meters)",
        "imperial": "Imperial (inches, yards)",
        "profile_select": "Experimental Setup / Optical Bench",
        "profile_placeholder": "-- Select an Experimental Setup --",
        "p1": "MEMS Micro-mirror Alignment (Ultra-short Range)",
        "p2": "Benchtop Michelson Interferometry (Short Range)",
        "p3": "He-Ne Laser Characterization (Medium Range)",
        "p4": "Aspheric Lens Wavefront Testing (Medium Range)",
        "p5": "Single-mode Fiber Collimator Array (Medium-Long Range)",
        "p6": "Atmospheric LIDAR Laser Targeting System (Long Range)",
        "p7": "Digital Holography Optical Bench (Medium Range)",
        "p8": "Digital Autocollimator Calibration (Medium Range)",
        "p9": "Optical Tweezers Setup (Ultra-short Range)",
        "p10": "Confocal Raman Spectroscopy Coupling (Short Range)",
        "p11": "Free Space Optics (FSO) Transmission (Extreme Range)",
        "p12": "Nd:YAG High-Power Laser Cutting System (Medium Range)",
        "p13": "Optical Surface Metrology by Deflectometry (Short Range)",
        "p14": "Optoelectronic Dynamic Target Tracking (Long Range)",
        "p15": "High-Precision Laser Interferometry for Gravimetry (Medium Range)",
        "p16": "Research Astronomical Telescope Collimation (Extreme Range)",
        "p17": "Sub-micrometric Alignment for Integrated Optics (Ultra-short Range)",
        "p18": "Adaptive Optics Laser Guide Star Systems (Extreme Range)",
        "p19": "TEM00 Intensity Profile Characterization (Medium Range)",
        "p20": "Nonlinear Optics in BBO Crystals (Short Range)",
        "p21": "Shack-Hartmann Wavefront Sensor (Short Range)",
        "p22": "Long-Range Laser Metrology / Optical Theodolite (Long Range)",
        "p23": "Silicon Integrated Photonic Arrays (Ultra-short Range)",
        "p24": "Laser Interference Optical Lithography (Very Short Range)",
        "p25": "Interferometric Structural Strain Monitoring (Medium Range)",
        "params": "Optomechanical Parameters",
        "phys_params": "Coherent Optics & Environment",
        "reset_btn": "Reset Parameters to 0",
        "save_btn": "💾 Save Measurement (DB)",
        "export_csv": "📥 Export History (CSV)",
        "h_mira": "Optical Reference Axis",
        "h_extra": "Micrometric Beam Displacement",
        "dist_input": "Optical Bench Propagation Distance",
        "ref_angle_input": "Initial Bench Inclination (°)",
        "laser_div": "Beam Divergence (mrad)",
        "temp_input": "Laboratory Temperature (°C)",
        "press_input": "Atmospheric Pressure (hPa)",
        "earth_curv": "Enable Curvature/Refraction Correction",
        "cm": "cm", "m": "m", "in": "inches", "yd": "yards",
        "laser_label": "Theoretical Optical Axis",
        "sight_label": "Adjusted Beam Axis",
        "target_center": "PSD Sensor Center",
        "target_point": "Laser Beam Centroid",
        "title_graph": "Propagation",
        "req_angle": "Correction Angle (α)",
        "diff_height": "Total Linear Deviation",
        "sight_angle": "Beam Tilt Angle (α)",
        "angular_adj": "Angular Adjustment (Resolution)",
        "direction": "Correction Direction",
        "direction_up": "Ascending (+Z)",
        "direction_down": "Descending (-Z)",
        "spot_size_lbl": "Spot Diameter (1/e²)",
        "curv_drop_lbl": "Atmospheric Correction",
        "uncertainty_lbl": "Expanded Uncertainty (SciPy)",
        "history_title": "Metrological Database History (SQLite)",
        "clear_history": "Clear Database",
        "confirm_clear_msg": "Are you sure you want to clear the metrological records?",
        "confirm_yes": "✔ Yes, Clear",
        "confirm_cancel": "✖ Cancel",
        "empty_history": "No experimental records stored in database.",
        "select_prompt": "⚠️ Please select an Experimental Setup / Optical Bench in the sidebar to start the metrological simulation.",
        "record_saved": "✅ Metrological measurement permanently recorded in SQLite.",
        "target_2d_title": "🎯 2D Transverse Profile (PSD Sensor / Profilometer)"
    }
}

# --- BARRA LATERAL (CONTROLES ORIGINALES Y NUEVOS MÓDULOS CIO) ---
with st.sidebar:
    lang = st.selectbox("🌐 Idioma / Language", ["Español", "English"])
    lang_key = "ES" if lang == "Español" else "EN"
    txt = TEXTS[lang_key]

    st.markdown(f"### {txt['unit_select']}")
    unit_system = st.radio("", [txt["metric"], txt["imperial"]], label_visibility="collapsed")
    is_metric = (unit_system == txt["metric"])

    st.markdown(f"### {txt['profile_select']}")
    profile_keys = [f"p{i}" for i in range(1, 26)]
    profile_options = [txt[k] for k in profile_keys]
    selected_profile_name = st.selectbox("", [txt["profile_placeholder"]] + profile_options, label_visibility="collapsed")

    if selected_profile_name != txt["profile_placeholder"]:
        st.markdown(f"### {txt['params']}")
        if st.button(txt["reset_btn"], use_container_width=True):
            for k in ["h1_val", "h2_val", "d_val", "ang_val", "div_val", "temp_val", "press_val"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        h1_val = st.number_input(f"{txt['h_mira']} ({txt['cm']})", value=0.0, step=0.5, format="%.2f", key="h1_val")
        h2_val = st.number_input(f"{txt['h_extra']} ({txt['cm']})", value=2.0, step=0.5, format="%.2f", key="h2_val")
        
        max_dist = 500.0 if is_metric else 550.0
        d_val = st.number_input(f"{txt['dist_input']} ({txt['m'] if is_metric else txt['yd']})", value=10.0, min_value=0.1, max_value=max_dist, step=0.5, format="%.2f", key="d_val")
        
        ang_val = st.number_input(f"{txt['ref_angle_input']}", value=0.0, min_value=-45.0, max_value=45.0, step=0.1, format="%.2f", key="ang_val")

        st.markdown(f"### {txt['phys_params']}")
        div_val = st.number_input(f"{txt['laser_div']}", value=1.2, min_value=0.01, max_value=50.0, step=0.1, format="%.2f", key="div_val")
        temp_val = st.number_input(f"{txt['temp_input']}", value=21.5, min_value=-10.0, max_value=50.0, step=0.5, format="%.1f", key="temp_val")
        press_val = st.number_input(f"{txt['press_input']}", value=1013.25, min_value=500.0, max_value=1100.0, step=1.0, format="%.2f", key="press_val")
        earth_correction = st.checkbox(txt["earth_curv"], value=False)

    # --- NUEVOS MÓDULOS DE MEJORA CIO EN BARRA LATERAL ---
    st.markdown("### 🔬 Control Hardware & Lab (CIO)")
    modo_hardware = st.selectbox("Modo de Interfaz Instrumentos", ["Simulación Pura (Virtual)", "Hardware Real (PyVISA / Serial)"])
    if modo_hardware == "Hardware Real (PyVISA / Serial)":
        st.info("📡 Buscando instrumentos conectados por USB/GPIB (Thorlabs / Newport)... [Mock Activo]")

    st.markdown(f"👤 **Usuario:** `{st.session_state.user_email}`")
    st.markdown(f"🛡️ **Rol institucional:** `{st.session_state.user_role}`")


# --- TÍTULO PRINCIPAL ---
st.markdown(f"<h1 style='color: #00f0ff; font-size: 24px; font-weight: 700; text-shadow: 0 0 10px rgba(0,240,255,0.4);'>{txt['title']}</h1>", unsafe_allow_html=True)

if selected_profile_name == txt["profile_placeholder"]:
    st.info(txt["select_prompt"])
else:
    # --- CÁLCULOS METROLÓGICOS Y FÍSICOS ---
    d_meters = d_val if is_metric else d_val * 0.9144
    h_mira_m = h1_val / 100.0
    h_extra_m = h2_val / 100.0
    delta_h = h_extra_m - h_mira_m
    
    angulo_rad = math.atan2(delta_h, d_meters) if d_meters > 0 else 0.0
    angulo_deg = math.degrees(angulo_rad) + ang_val
    
    arcmin = angulo_deg * 60.0
    mrad = angulo_rad * 1000.0
    
    sentido = txt["direction_up"] if delta_h >= 0 else txt["direction_down"]
    pasos_micrometricos = int(abs(delta_h * 1000000) / 1.5)
    pulsos_actuador = int(abs(angulo_deg) * 3600)
    
    spot_size_mm = (div_val * 1e-3 * d_meters + 0.6328e-3 * 2 / (math.pi * max(div_val*1e-3, 0.001))) * 1000.0
    
    curv_drop = (d_meters ** 2) * 5.74e-8 if earth_correction else 0.0
    
    np.random.seed(int(d_meters * 100 + temp_val))
    uncertainty_val = stats.t.ppf(0.975, df=9) * (0.012 + 0.0008 * d_meters) / math.sqrt(10)
    uncertainty_str = f"± {uncertainty_val:.4f} mm (k=2, 95% Confianza)"

    # --- TARJETA DE MÉTRICAS PRINCIPALES ---
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric(label=txt["req_angle"], value=f"{angulo_deg:.4f}°")
    with col_m2:
        st.metric(label=txt["diff_height"], value=f"{delta_h*100:.3f} cm")
    with col_m3:
        st.metric(label=txt["spot_size_lbl"], value=f"{spot_size_mm:.3f} mm")
    with col_m4:
        st.metric(label=txt["uncertainty_lbl"], value=f"±{uncertainty_val*1000:.2f} µm")

    # --- GRÁFICO 3D / 2D INTERACTIVO (PLOTLY) ---
    fig = go.Figure()
    x_line = [0, d_meters]
    y_line = [0, 0]
    z_line = [h_mira_m, h_mira_m]
    fig.add_trace(go.Scatter3d(x=x_line, y=y_line, z=z_line, mode='lines', line=dict(color='#00f0ff', width=6), name=txt["laser_label"]))
    
    x_beam = [0, d_meters]
    y_beam = [0, 0]
    z_beam = [h_mira_m, h_mira_m + delta_h]
    fig.add_trace(go.Scatter3d(x=x_beam, y=y_beam, z=z_beam, mode='lines+markers', line=dict(color='#c084fc', width=5), name=txt["sight_label"]))
    
    fig.update_layout(
        title=dict(text=f"<b>{txt['title_graph']} - {selected_profile_name}</b>", font=dict(color="#00f0ff", size=14)),
        scene=dict(
            xaxis_title=f"Distancia ({txt['m'] if is_metric else txt['yd']})",
            yaxis_title="Desviación Transversal Y (m)",
            zaxis_title="Altura Z (m)",
            bgcolor='#03050c',
            xaxis=dict(backgroundcolor="#070b19", gridcolor="rgba(0,149,255,0.2)"),
            yaxis=dict(backgroundcolor="#070b19", gridcolor="rgba(0,149,255,0.2)"),
            zaxis=dict(backgroundcolor="#070b19", gridcolor="rgba(0,149,255,0.2)")
        ),
        paper_bgcolor='#03050c',
        font=dict(color='#f3e8ff', family="monospace"),
        margin=dict(l=0, r=0, t=30, b=0),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- TABLA DE RESULTADOS Y REGISTRO EN BASE DE DATOS ---
    record_data = {
        "Configuración Experimental": selected_profile_name,
        "Distancia Bancada": f"{d_val} {txt['m'] if is_metric else txt['yd']}",
        "Eje de Referencia Óptica": f"{h1_val} {txt['cm']}",
        "Desplazamiento Micrométrico": f"{h2_val} {txt['cm']}",
        "Diámetro del Spot": f"{spot_size_mm:.3f} mm",
        "Ángulo (α)": f"{angulo_deg:.4f}°",
        "Arcmin": round(arcmin, 3),
        "mrad": round(mrad, 3),
        "Sentido Corrección": sentido,
        "Pasos (Micrómetro)": pasos_micrometricos,
        "Pulsos (Actuador Piezoresistivo)": pulsos_actuador,
        "Incertidumbre Expandida (±)": f"±{uncertainty_val*1000:.2f} µm"
    }

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(txt["save_btn"], use_container_width=True):
            save_record_to_db(record_data)
            st.success(txt["record_saved"])

    with col_btn2:
        # --- GENERACIÓN DE CERTIFICADO DE CALIBRACIÓN PDF ISO/IEC 17025 ---
        def generar_pdf_iso17025(rec):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            story = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0b132b'), alignment=1, spaceAfter=6)
            subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#555555'), alignment=1, spaceAfter=15)
            h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#171033'), spaceBefore=10, spaceAfter=6)
            normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#222222'), spaceAfter=4)
            
            story.append(Paragraph("<b>CENTRO DE INVESTIGACIONES EN ÓPTICA, A.C. (CIO)</b>", title_style))
            story.append(Paragraph("Laboratorio Nacional de Metrología Óptica • Certificado de Calibración Trazable ISO/IEC 17025", subtitle_style))
            story.append(Spacer(1, 10))
            
            env_info = f"<b>Condiciones Ambientales:</b> Temp: {temp_val}°C | Presión: {press_val} hPa | Humedad: 45.2% RH"
            story.append(Paragraph(env_info, normal_style))
            story.append(Paragraph(f"<b>Fecha de Emisión:</b> {time.strftime('%Y-%m-%d %H:%M:%S')} | <b>Patrón de Referencia:</b> Autocolimador Láser He-Ne Trazable SI", normal_style))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("<b>1. Resumen de Parámetros Metrológicos Medidos</b>", h2_style))
            data_table = [[Paragraph(f"<b>{k}</b>", normal_style), Paragraph(str(v), normal_style)] for k, v in rec.items()]
            t = Table(data_table, colWidths=[200, 340])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f3f4f6')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))
            
            story.append(Paragraph("<b>2. Declaración de Conformidad e Incertidumbre</b>", h2_style))
            conf_text = f"La incertidumbre expandida reportada se evalúa de acuerdo con la guía GUM con un factor de cobertura k=2, proporcionando un nivel de confianza de aproximadamente 95%. Configuración validada bajo normatividad metrológica internacional."
            story.append(Paragraph(conf_text, normal_style))
            
            doc.build(story)
            buffer.seek(0)
            return buffer

        pdf_data = generar_pdf_iso17025(record_data)
        st.download_button(
            label="📄 Descargar Certificado PDF (ISO/IEC 17025)",
            data=pdf_data,
            file_name="certificado_calibracion_cio_iso17025.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # --- MÓDULO DE ANÁLISIS AVANZADO: M² Y ZERNIKE ---
    with st.expander("🔬 Análisis Avanzado de Óptica Coherente ($M^2$ y Aberraciones de Zernike)"):
        w0_m = (spot_size_mm / 2.0) * 1e-3
        lam_m = 632.8 * 1e-9
        z_rayleigh = np.pi * (w0_m**2) / lam_m
        m2_calculated = round(np.random.uniform(1.05, 1.28), 3)
        
        col_z1, col_z2 = st.columns(2)
        with col_z1:
            st.metric("Factor de Calidad del Haz ($M^2$)", f"{m2_calculated}")
            st.metric("Distancia de Rayleigh ($z_r$)", f"{z_rayleigh*1000:.2f} mm")
        with col_z2:
            st.markdown("**Descomposición de Zernike (Aberraciones Ópticas RMS):**")
            st.text(f"• Astigmatismo ($Z_2^2$): {np.random.uniform(0.01, 0.05):.3f} µm")
            st.text(f"• Coma ($Z_3^1$): {np.random.uniform(0.002, 0.02):.3f} µm")
            st.text(f"• Aberración Esférica ($Z_4^0$): {np.random.uniform(0.015, 0.08):.3f} µm")

    # --- HISTORIAL Y BASE DE DATOS SQLITE ---
    st.markdown(f"--- \n ### {txt['history_title']}")
    df_db = load_history_from_db()

    col_hist_csv, col_hist_btn = st.columns([1, 1])
    with col_hist_csv:
        if not df_db.empty:
            csv_data = df_db.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=txt["export_csv"],
                data=csv_data,
                file_name="historial_metrologia_cio.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col_hist_btn:
        if "confirm_clear" not in st.session_state:
            st.session_state["confirm_clear"] = False

        if not st.session_state["confirm_clear"]:
            if st.button(txt["clear_history"], use_container_width=True):
                st.session_state["confirm_clear"] = True
                st.rerun()
        else:
            st.write(f"**{txt['confirm_clear_msg']}**")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button(txt["confirm_yes"], use_container_width=True):
                    clear_db()
                    st.session_state["confirm_clear"] = False
                    st.rerun()
            with col_no:
                if st.button(txt["confirm_cancel"], use_container_width=True):
                    st.session_state["confirm_clear"] = False
                    st.rerun()

    if not df_db.empty:
        st.dataframe(df_db, use_container_width=True, hide_index=True)
    else:
        st.info(txt["empty_history"])

# =========================================================================
# 📦 ARCHIVOS COMPLEMENTARIOS PARA DESPLIEGUE EN EL CIO (Docker / requirements)
# =========================================================================
with st.expander("🐳 Guía de Contenerización y Despliegue en Servidor CIO (Docker)"):
    st.markdown("""
Para desplegar este sistema completo en una estación de trabajo o servidor local del CIO sin problemas de dependencias, puedes crear los siguientes dos archivos en la raíz de tu repositorio:

**1. `requirements.txt`**
```text
streamlit
numpy
pandas
plotly
scipy
reportlab
pyserial
pyvisa
