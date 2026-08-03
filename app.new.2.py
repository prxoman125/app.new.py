import streamlit as st
import numpy as np
import math
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import time
from scipy import stats

# 1. Configuración de la página (SIEMPRE PRIMERO EN STREAMLIT)
st.set_page_config(
    page_title="Plataforma Institucional de Metrología y Alineación Optomecánica | CIO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# MÓDULO DE AUTENTICACIÓN INSTITUCIONAL DE ACCESO RESTRINGIDO
# =========================================================================

USUARIOS_PERMITIDOS = [
    "j3remyx1010@gmail.com",
    "correo2@ejemplo.com"
]

CONTRASEÑA_CORRECTA = "Jggg101031"
MAX_INTENTOS = 3

if "intentos" not in st.session_state:
    st.session_state.intentos = 0
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if st.session_state.intentos >= MAX_INTENTOS:
    st.error("Acceso denegado. Se ha superado el número máximo de intentos permitidos.")
    st.stop()

if not st.session_state.autenticado:
    st.markdown("""
        <style>
            header, [data-testid="stHeader"] {
                visibility: hidden;
                height: 0px;
            }
            .stApp {
                background-color: #0A0C0B !important;
                overflow-x: hidden;
            }

            /* Fondo Monocromático Dinámico con Patrón Geométrico Sutil */
            .grid-bg {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: 
                    linear-gradient(rgba(31, 36, 33, 0.04) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(31, 36, 33, 0.04) 1px, transparent 1px);
                background-size: 40px 40px;
                animation: gridMove 30s linear infinite;
                z-index: 0;
                pointer-events: none;
            }

            .top-global-hud {
                position: fixed;
                top: 20px; left: 30px; right: 30px;
                display: flex;
                justify-content: space-between;
                font-family: 'Courier New', Courier, monospace;
                font-size: 11px;
                color: #8C9490;
                letter-spacing: 2px;
                z-index: 10;
                opacity: 0.8;
                pointer-events: none;
            }

            .login-wrapper {
                position: relative;
                max-width: 440px;
                margin: 8vh auto 0 auto;
                padding: 1px;
                border-radius: 12px;
                background: linear-gradient(135deg, #2D3330, #1F2421, #0A0C0B);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
            }

            .login-card {
                position: relative;
                background: rgba(13, 16, 14, 0.96);
                backdrop-filter: blur(12px);
                border-radius: 11px;
                padding: 35px 30px 25px 30px;
                z-index: 2;
            }

            .login-title {
                color: #F1F3F2;
                font-size: 16px;
                font-weight: 600;
                text-align: center;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                margin: 0 0 8px 0;
            }
            .login-subtitle {
                color: #8C9490;
                font-size: 10px;
                text-align: center;
                letter-spacing: 1px;
                margin-bottom: 25px;
                font-family: 'Courier New', Courier, monospace;
                text-transform: uppercase;
            }

            @keyframes gridMove {
                0% { background-position: 0 0, 0 0; }
                100% { background-position: 40px 40px, 40px 40px; }
            }
        </style>

        <div class="grid-bg"></div>

        <div class="top-global-hud">
            <span>CENTRO DE INVESTIGACIONES EN ÓPTICA - LEÓN, GTO.</span>
            <span>SISTEMA DE GESTIÓN METROLÓGICA</span>
        </div>
    """, unsafe_allow_html=True)
    
    _, col_center, _ = st.columns([1, 1.2, 1])
    
    with col_center:
        st.markdown("""
            <div class="login-wrapper">
                <div class="login-card">
                    <div class="login-title">Autenticación de Acceso</div>
                    <div class="login-subtitle">Plataforma de Ingenierías Optomecánicas</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("formulario_login"):
            correo = st.text_input("Credencial Institucional (Correo Electrónico):", placeholder="usuario@cio.mx")
            password = st.text_input("Clave de Acceso:", type="password", placeholder="••••••••") 
            boton_ingresar = st.form_submit_button("Validar Credenciales", use_container_width=True)
            
            if boton_ingresar:
                correo_ingresado = correo.strip().lower()
                lista_permitidos = [u.strip().lower() for u in USUARIOS_PERMITIDOS]
                
                if correo_ingresado in lista_permitidos and password == CONTRASEÑA_CORRECTA:
                    st.session_state.autenticado = True
                    st.session_state.intentos = 0
                    
                    with st.spinner("Estableciendo enlace seguro con transductores y cargando matrices de calibración..."):
                        time.sleep(1.0)
                    st.rerun()
                else:
                    st.session_state.intentos += 1
                    intentos_restantes = MAX_INTENTOS - st.session_state.intentos
                    st.error(f"Credenciales no válidas. Intentos restantes: {intentos_restantes}")
                    st.stop()

if not st.session_state.autenticado:
    st.stop()


# =========================================================================
# BANCO DE SIMULACIÓN METROLÓGICA (ESTÉTICA MONOCROMÁTICA NEÓN OSCURO)
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

# --- ESTILOS CSS MONOCROMÁTICOS AVANZADOS (NEO-DARK PALETTE) ---
st.markdown("""
    <style>
        header, [data-testid="stHeader"], [data-testid="stToolbar"] {
            visibility: hidden !important;
            height: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
        }

        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
            animation: fadeIn 0.6s ease-out;
        }

        .stApp {
            background-color: #0A0C0B !important;
            color: #F1F3F2 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        [data-testid="stSidebar"] {
            background-color: #121513 !important;
            border-right: 1px solid #1F2421 !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.5rem !important;
        }

        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #F1F3F2 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 18px !important;
            margin-bottom: 8px !important;
            border-bottom: 1px solid #1F2421 !important;
            padding-bottom: 4px;
        }

        div.stButton > button {
            background: #1F2421 !important;
            color: #F1F3F2 !important;
            border: 1px solid #2D3330 !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            font-size: 13px !important;
            transition: all 0.25s ease !important;
        }
        div.stButton > button:hover {
            background: #2D3330 !important;
            border-color: #8C9490 !important;
            color: #FFFFFF !important;
            transform: translateY(-1px);
        }

        div[data-baseweb="input"], div[data-baseweb="select"] > div {
            background-color: #121513 !important;
            border: 1px solid #1F2421 !important;
            color: #F1F3F2 !important;
            border-radius: 6px !important;
        }

        div[data-baseweb="input"]:hover, div[data-baseweb="select"] > div:hover {
            border-color: #2D3330 !important;
        }

        .metric-card-container {
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: #121513;
            border: 1px solid #1F2421; 
            padding: 16px 20px; 
            border-radius: 8px; 
            margin-top: 15px; 
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

TEXTS = {
    "ES": {
        "title": "Centro de Investigaciones en Óptica (CIO) | Sistema de Alineación Optomecánica",
        "lang_select": "Idioma Institucional",
        "unit_select": "Sistema Dimensional",
        "metric": "Métrico (Centímetros, Metros)",
        "imperial": "Imperial (Pulgadas, Yardas)",
        "profile_select": "Línea Experimental de Investigación",
        "profile_placeholder": "-- Seleccione la Disciplina Experimental --",
        
        # Carreras actualizadas y especializadas (Sin etiquetas de rango)
        "p1": "Ingeniería de Micro-sistemas MEMS y Dispositivos Difractivos",
        "p2": "Interferometría Láser de Alta Coherencia y Fase Óptica",
        "p3": "Caracterización Espectrofotométrica de Láseres de Estado Sólido",
        "p4": "Metrología de Superficies Asféricas y Frente de Onda",
        "p5": "Diseño y Acoplamiento de Arreglos Fotónicos Monomodo",
        "p6": "Sistemas de Percepción Láser Remoto LIDAR Atmosférico",
        "p7": "Óptica Coherente y Holografía Computacional Digital",
        "p8": "Calibración Metrológica de Instrumentación Autocolimadora",
        "p9": "Micro-manipulación por Fuerzas de Gradiente Óptico",
        "p10": "Espectroscopía Raman Confocal de Alta Resolución Espacial",
        "p11": "Comunicaciones Ópticas en Espacio Libre FSO de Gran Cobertura",
        "p12": "Sistemas Láser de Potencia para Manufactura de Materiales Avanzados",
        "p13": "Topografía Óptica Superficial mediante Deflectometría Dinámica",
        "p14": "Seguimiento Optoelectrónico de Blancos en Trayectoria Variable",
        "p15": "Interferometría de Alta Estabilidad para Gravimetría Geofísica",
        "p16": "Alineación de Óptica Astronómica y Telescopios de Investigación",
        "p17": "Nanofabricación y Alineación Sub-micrométrica en Óptica Integrada",
        "p18": "Sistemas de Guía Láser para Corrección de Aberraciones Atmosféricas",
        "p19": "Análisis Matricial de Modos Transversales y Perfiles de Intensidad",
        "p20": "Óptica No Lineal y Generación de Armónicos en Cristales BBO",
        "p21": "Sensores de Frente de Onda de Alta Dinámica Shack-Hartmann",
        "p22": "Geodesia Óptica de Precisión y Metrología de Grandes Distancias",
        "p23": "Circuitos Fotónicos Integrados en Sustratos de Silicio",
        "p24": "Litografía de Interferencia Coherente y Nanoestructuración",
        "p25": "Monitoreo Interferométrico de Deformación en Estructuras Complejas",

        "params": "Parámetros de Configuración Óptica",
        "phys_params": "Variables Ambientales y Coherencia",
        "reset_btn": "Restablecer Parámetros",
        "save_btn": "Registrar Medición en Base de Datos",
        "export_csv": "Exportar Registros (CSV)",
        "h_mira": "Eje Óptico de Referencia",
        "h_extra": "Desplazamiento Lineal Micrométrico",
        "dist_input": "Longitud de Propagación en Banco",
        "ref_angle_input": "Inclinación Inicial del Banco (°)",
        "laser_div": "Divergencia del Haz (mrad)",
        "temp_input": "Temperatura del Laboratorio (°C)",
        "press_input": "Presión Atmosférica (hPa)",
        "earth_curv": "Corrección por Refracción Atmosférica y Geometría Terrestre",
        "cm": "cm",
        "m": "m",
        "in": "in",
        "yd": "yd",
        "laser_label": "Eje Teórico de Propagación",
        "sight_label": "Eje del Haz Corregido",
        "target_center": "Centro del Sensor PSD",
        "target_point": "Centroide del Spot",
        "title_graph": "Propagación Tridimensional del Haz",
        "req_angle": "Ángulo de Corrección (α)",
        "diff_height": "Desviación Lineal Total",
        "sight_angle": "Inclinación del Haz (α)",
        "angular_adj": "Resolución de Ajuste Angular",
        "direction": "Sentido de Corrección",
        "direction_up": "Ascendente (+Z)",
        "direction_down": "Descendente (-Z)",
        "spot_size_lbl": "Diámetro de Cintura (1/e²)",
        "curv_drop_lbl": "Corrección Atmosférica",
        "uncertainty_lbl": "Incertidumbre Expandida (SciPy)",
        "history_title": "Historial de Registros Metrológicos (SQLite)",
        "clear_history": "Vaciar Base de Datos",
        "confirm_clear_msg": "Confirme la eliminación permanente del registro metrológico:",
        "confirm_yes": "Confirmar Eliminación",
        "confirm_cancel": "Cancelar Operación",
        "empty_history": "No existen registros experimentales almacenados en la base de datos.",
        "select_prompt": "Seleccione una Línea Experimental de Investigación en el panel lateral para inicializar el sistema de simulación.",
        "record_saved": "Medición registrada exitosamente en el sistema SQLite.",
        "target_2d_title": "Perfil Transversal de Distribución Energética (Sensor PSD)"
    },
    "EN": {
        "title": "Optics Research Center (CIO) | Optomechanical Alignment System",
        "lang_select": "Institutional Language",
        "unit_select": "Dimensional System",
        "metric": "Metric (Centimeters, Meters)",
        "imperial": "Imperial (Inches, Yards)",
        "profile_select": "Experimental Research Line",
        "profile_placeholder": "-- Select Experimental Discipline --",
        
        "p1": "MEMS Micro-systems and Diffractive Devices Engineering",
        "p2": "High Coherence Laser Interferometry and Optical Phase",
        "p3": "Spectrophotometric Characterization of Solid-State Lasers",
        "p4": "Aspheric Surface Metrology and Wavefront Analysis",
        "p5": "Single-mode Photonic Array Design and Coupling",
        "p6": "Atmospheric LIDAR Remote Laser Sensing Systems",
        "p7": "Coherent Optics and Digital Computational Holography",
        "p8": "Metrological Calibration of Autocollimating Instrumentation",
        "p9": "Optical Gradient Force Micro-manipulation",
        "p10": "High Spatial Resolution Confocal Raman Spectroscopy",
        "p11": "Large Coverage Free Space Optics (FSO) Communications",
        "p12": "High-Power Laser Systems for Advanced Material Manufacturing",
        "p13": "Surface Optical Topography via Dynamic Deflectometry",
        "p14": "Optoelectronic Target Tracking in Variable Trajectories",
        "p15": "High Stability Interferometry for Geophysical Gravimetry",
        "p16": "Astronomical Optics and Research Telescope Alignment",
        "p17": "Sub-micrometric Nanofabrication and Alignment in Integrated Optics",
        "p18": "Laser Guide Star Systems for Atmospheric Aberration Correction",
        "p19": "Transverse Mode Matrix Analysis and Intensity Profiles",
        "p20": "Nonlinear Optics and Harmonic Generation in BBO Crystals",
        "p21": "High Dynamics Shack-Hartmann Wavefront Sensors",
        "p22": "Precision Optical Geodesy and Long-Range Metrology",
        "p23": "Silicon Substrate Integrated Photonic Circuits",
        "p24": "Coherent Interference Lithography and Nano-structuring",
        "p25": "Interferometric Strain Monitoring in Complex Structures",

        "params": "Optical Configuration Parameters",
        "phys_params": "Environmental Variables and Coherence",
        "reset_btn": "Reset Parameters",
        "save_btn": "Log Measurement to Database",
        "export_csv": "Export Records (CSV)",
        "h_mira": "Optical Reference Axis",
        "h_extra": "Micrometric Linear Displacement",
        "dist_input": "Optical Bench Propagation Length",
        "ref_angle_input": "Initial Bench Inclination (°)",
        "laser_div": "Beam Divergence (mrad)",
        "temp_input": "Laboratory Temperature (°C)",
        "press_input": "Atmospheric Pressure (hPa)",
        "earth_curv": "Atmospheric Refraction and Terrestrial Curvature Correction",
        "cm": "cm",
        "m": "m",
        "in": "in",
        "yd": "yd",
        "laser_label": "Theoretical Propagation Axis",
        "sight_label": "Corrected Beam Axis",
        "target_center": "PSD Sensor Center",
        "target_point": "Spot Centroid",
        "title_graph": "Three-Dimensional Beam Propagation",
        "req_angle": "Correction Angle (α)",
        "diff_height": "Total Linear Deviation",
        "sight_angle": "Beam Inclination (α)",
        "angular_adj": "Angular Adjustment Resolution",
        "direction": "Correction Sense",
        "direction_up": "Ascending (+Z)",
        "direction_down": "Descending (-Z)",
        "spot_size_lbl": "Beam Waist Diameter (1/e²)",
        "curv_drop_lbl": "Atmospheric Correction",
        "uncertainty_lbl": "Expanded Uncertainty (SciPy)",
        "history_title": "Metrological Database Records (SQLite)",
        "clear_history": "Clear Database",
        "confirm_clear_msg": "Confirm permanent deletion of the metrological records:",
        "confirm_yes": "Confirm Deletion",
        "confirm_cancel": "Cancel Operation",
        "empty_history": "No experimental records stored in the database.",
        "select_prompt": "Select an Experimental Research Line in the sidebar to initialize the simulation system.",
        "record_saved": "Measurement successfully recorded in the SQLite system.",
        "target_2d_title": "Transverse Energy Distribution Profile (PSD Sensor)"
    }
}

st.sidebar.header("Configuración General")
lang = st.sidebar.selectbox("Idioma Institucional", ["Español", "English"])
lang_code = "ES" if lang == "Español" else "EN"
txt = TEXTS[lang_code]

st.sidebar.header(txt["profile_select"])
profiles_options = [txt["profile_placeholder"]] + [
    txt["p1"], txt["p2"], txt["p3"], txt["p4"], txt["p5"], txt["p6"],
    txt["p7"], txt["p8"], txt["p9"], txt["p10"], txt["p11"], txt["p12"],
    txt["p13"], txt["p14"], txt["p15"], txt["p16"], txt["p17"], txt["p18"],
    txt["p19"], txt["p20"], txt["p21"], txt["p22"], txt["p23"], txt["p24"], txt["p25"]
]

profile = st.sidebar.selectbox(txt["profile_select"], profiles_options, index=0)

PROFILE_PRESETS = {
    txt["p1"]:  (True,  1.2,   0.15,  1.5,   0.05, 0.5),
    txt["p2"]:  (True,  2.5,   0.50,  6.0,   0.20, 0.8),
    txt["p3"]:  (False, 4.0,   1.50,  120.0, 1.20, 1.2),
    txt["p4"]:  (True,  12.0,  4.50,  350.0, 2.80, 1.5),
    txt["p5"]:  (True,  8.0,  -2.10,  650.0, -1.50, 1.0),
    txt["p6"]:  (True,  25.0, -8.00,  1200.0, 3.50, 2.0),
    txt["p7"]:  (False, 10.0,  3.20,  850.0, 2.10, 1.4),
    txt["p8"]:  (True,  4.5,   0.80,  180.0, 0.45, 1.0),
    txt["p9"]:  (True,  3.0,   1.20,  18.0,  2.50, 0.6),
    txt["p10"]: (True,  0.5,   0.05,  2.5,   0.10, 0.3),
    txt["p11"]: (True,  35.0,  12.00, 1500.0, 8.50, 0.8),
    txt["p12"]: (False, 5.0,  -1.80,  320.0, -2.10, 1.2),
    txt["p13"]: (True,  5.0,  -1.20,  12.0,  -0.80, 0.9),
    txt["p14"]: (True,  15.0,  2.80,  75.0,   0.90, 1.1),
    txt["p15"]: (False, 6.0,  -2.50,  1100.0,-4.20, 2.5),
    txt["p16"]: (True,  45.0,  15.00, 2000.0, 12.00, 0.2),
    txt["p17"]: (True,  0.2,   0.04,  0.8,   0.05, 0.1),
    txt["p18"]: (True,  50.0, -10.00, 1800.0,-14.00, 0.5),
    txt["p19"]: (True,  6.5,   1.10,  80.0,  1.50, 1.8),
    txt["p20"]: (True,  1.8,  -0.30,  12.0,  -0.40, 0.4),
    txt["p21"]: (True,  0.9,   0.12,  4.5,   0.25, 0.5),
    txt["p22"]: (False, 14.0,  4.50,  650.0, 3.80, 1.3),
    txt["p23"]: (True,  2.8,  -0.50,  45.0,  -1.20, 1.5),
    txt["p24"]: (True,  0.1,   0.01,  0.3,   0.02, 0.05),
    txt["p25"]: (True,  20.0,  4.20,  220.0, 2.90, 1.0),
}

if "current_profile" not in st.session_state:
    st.session_state["current_profile"] = profile

if profile != st.session_state["current_profile"]:
    st.session_state["current_profile"] = profile
    if profile in PROFILE_PRESETS:
        pref_metric, h_m, h_e, dist, angle, div_mrad = PROFILE_PRESETS[profile]
        st.session_state["unit_choice"] = txt["metric"] if pref_metric else txt["imperial"]
        st.session_state["h_mira_val"] = h_m
        st.session_state["h_extra_val"] = h_e
        st.session_state["dist_val"] = dist
        st.session_state["ref_angle_val"] = angle
        st.session_state["laser_div_val"] = div_mrad
    else:
        st.session_state["h_mira_val"] = 0.0
        st.session_state["h_extra_val"] = 0.0
        st.session_state["dist_val"] = 0.0
        st.session_state["ref_angle_val"] = 0.0
        st.session_state["laser_div_val"] = 1.0

if "unit_choice" not in st.session_state:
    st.session_state["unit_choice"] = txt["metric"]

unit_sys = st.sidebar.radio(txt["unit_select"], [txt["metric"], txt["imperial"]], key="unit_choice")
is_metric = (unit_sys == txt["metric"])

if "h_mira_val" not in st.session_state: st.session_state["h_mira_val"] = 0.0
if "h_extra_val" not in st.session_state: st.session_state["h_extra_val"] = 0.0
if "dist_val" not in st.session_state: st.session_state["dist_val"] = 0.0
if "ref_angle_val" not in st.session_state: st.session_state["ref_angle_val"] = 0.0
if "laser_div_val" not in st.session_state: st.session_state["laser_div_val"] = 1.0
if "temp_val" not in st.session_state: st.session_state["temp_val"] = 20.0
if "press_val" not in st.session_state: st.session_state["press_val"] = 1013.25
if "earth_curv_val" not in st.session_state: st.session_state["earth_curv_val"] = False
if "confirm_clear" not in st.session_state: st.session_state["confirm_clear"] = False

def reset_inputs_to_zero():
    st.session_state["h_mira_val"] = 0.0
    st.session_state["h_extra_val"] = 0.0
    st.session_state["dist_val"] = 0.0
    st.session_state["ref_angle_val"] = 0.0
    st.session_state["laser_div_val"] = 1.0

st.sidebar.header(txt["params"])

if is_metric:
    h_unit, d_unit = txt["cm"], txt["m"]
else:
    h_unit, d_unit = txt["in"], txt["yd"]

H_mira = st.sidebar.number_input(f"{txt['h_mira']} ({h_unit})", min_value=-500.0, max_value=500.0, value=st.session_state["h_mira_val"], step=0.1, key="h_mira_val")
H_extra = st.sidebar.number_input(f"{txt['h_extra']} ({h_unit})", min_value=-500.0, max_value=500.0, value=st.session_state["h_extra_val"], step=0.1, key="h_extra_val")
D_val = st.sidebar.number_input(f"{txt['dist_input']} ({d_unit})", min_value=0.0, max_value=2000.0, value=st.session_state["dist_val"], step=1.0, key="dist_val")
ref_angle_deg = st.sidebar.number_input(txt['ref_angle_input'], min_value=-30.00, max_value=30.00, value=st.session_state["ref_angle_val"], step=0.10, format="%.2f", key="ref_angle_val")

st.sidebar.header(txt["phys_params"])
laser_div_mrad = st.sidebar.number_input(txt["laser_div"], min_value=0.01, max_value=10.0, value=st.session_state["laser_div_val"], step=0.1, key="laser_div_val")
temp_c = st.sidebar.number_input(txt["temp_input"], min_value=-40.0, max_value=60.0, value=st.session_state["temp_val"], step=1.0, key="temp_val")
press_hpa = st.sidebar.number_input(txt["press_input"], min_value=500.0, max_value=1100.0, value=st.session_state["press_val"], step=10.0, key="press_val")
use_earth_curv = st.sidebar.checkbox(txt["earth_curv"], value=st.session_state["earth_curv_val"], key="earth_curv_val")

save_clicked = st.sidebar.button(txt["save_btn"], use_container_width=True)
st.sidebar.button(txt["reset_btn"], on_click=reset_inputs_to_zero, use_container_width=True)

if is_metric:
    D_m = D_val
    D_cm, H_mira_cm, H_extra_cm = D_val * 100, H_mira, H_extra
else:
    D_m = D_val * 0.9144
    D_cm, H_mira_cm, H_extra_cm = D_val * 91.44, H_mira * 2.54, H_extra * 2.54

# --- ENCABEZADO INSTITUCIONAL ---
st.markdown(f"""
    <div style="background: #121513;
                padding: 16px 25px;
                border-radius: 8px;
                border-left: 4px solid #8C9490;
                border: 1px solid #1F2421;
                margin-bottom: 20px;">
        <h2 style="color: #F1F3F2; margin: 0; font-size: 20px; font-weight: 600; letter-spacing: 0.5px;">
            {txt['title']}
        </h2>
        <p style="color: #8C9490; margin: 4px 0 0 0; font-size: 12px;">
            Centro de Investigaciones en Óptica, A.C. (CIO) — León, Guanajuato | Línea Experimental: <b style="color: #F1F3F2;">{profile if profile != txt['profile_placeholder'] else 'Ninguna'}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

if profile == txt["profile_placeholder"]:
    st.warning(txt["select_prompt"])
    st.stop()

# --- CÁLCULOS FÍSICOS Y DE INCERTIDUMBRE (SciPy) ---
R_earth_m = 6371000.0
k_refraction = 0.14
if use_earth_curv and D_m > 0:
    R_eff = R_earth_m / (1 - k_refraction)
    curv_drop_cm = ((D_m ** 2) / (2 * R_eff)) * 100
else:
    curv_drop_cm = 0.0

n_air = 1 + (77.6e-6 * press_hpa / (temp_c + 273.15))
refraction_factor = (n_air - 1.00027) * 10.0

div_rad = laser_div_mrad / 1000.0
spot_diameter_cm = 0.2 + (2.0 * D_m * math.tan(div_rad / 2.0) * 100.0)
spot_radius_cm = spot_diameter_cm / 2.0

ref_angle_rad = math.radians(ref_angle_deg)
y_ref_end = D_cm * math.tan(ref_angle_rad)
y_target_point = y_ref_end + H_extra_cm - curv_drop_cm
diferencia_altura_cm = y_target_point - H_mira_cm

if D_cm > 0:
    angulo_rad = math.atan(diferencia_altura_cm / D_cm)
else:
    angulo_rad = 0.0

angulo_deg = math.degrees(angulo_rad)
arcmin, mrad = angulo_deg * 60, angulo_rad * 1000
diff_height_display = diferencia_altura_cm if is_metric else diferencia_altura_cm / 2.54
spot_size_display = spot_diameter_cm if is_metric else spot_diameter_cm / 2.54
curv_drop_display = curv_drop_cm if is_metric else curv_drop_cm / 2.54

delta_h_cm = 0.05
delta_d_cm = 50.0 if D_m > 0 else 0.1
if D_cm > 0:
    sigma_angle_rad = math.sqrt((delta_h_cm / D_cm)**2 + (diferencia_altura_cm * delta_d_cm / (D_cm**2 + diferencia_altura_cm**2))**2)
    confidence_factor = stats.norm.ppf(0.975)
    uncertainty_mrad = sigma_angle_rad * 1000.0 * confidence_factor
    uncertainty_arcmin = math.degrees(sigma_angle_rad) * 60.0 * confidence_factor
else:
    uncertainty_mrad = 0.0
    uncertainty_arcmin = 0.0

uncertainty_str = f"±{uncertainty_mrad:.2f} mrad (95% IC)"

is_up = (angulo_deg >= 0)
direccion_str = txt["direction_up"] if is_up else txt["direction_down"]

pasos_micrometricos = abs(round(arcmin * 4))
pulsos_actuador = abs(round(mrad * 10))

if save_clicked:
    current_record = {
        "Configuración Experimental": profile,
        "Distancia Bancada": f"{D_val:.1f} {d_unit}",
        "Eje de Referencia Óptica": f"{H_mira:.2f} {h_unit}",
        "Desplazamiento Micrométrico": f"{H_extra:.2f} {h_unit}",
        "Diámetro del Spot": f"{spot_size_display:.2f} {h_unit}",
        "Ángulo (α)": f"{angulo_deg:.4f}°",
        "Arcmin": arcmin,
        "mrad": mrad,
        "Sentido Corrección": direccion_str,
        "Pasos (Micrómetro)": pasos_micrometricos,
        "Pulsos (Actuador Piezoresistivo)": pulsos_actuador,
        "Incertidumbre Expandida (±)": uncertainty_str
    }
    save_record_to_db(current_record)
    st.sidebar.success(txt["record_saved"])

# --- VISUALIZACIÓN GRÁFICA (PLOTS MONOCROMÁTICOS) ---
col_3d, col_2d = st.columns([1.75, 1.0])

with col_3d:
    pos_mira = (0, H_mira_cm)
    pos_impacto_mira = (D_cm, y_target_point)

    fig3d = go.Figure()

    grid_x = np.linspace(0, max(D_cm, 10), 10)
    grid_y = np.linspace(-max(abs(H_extra_cm)*1.5, 20), max(abs(H_extra_cm)*1.5, 20), 10)
    gx, gy = np.meshgrid(grid_x, grid_y)
    gz = np.zeros_like(gx)

    fig3d.add_trace(go.Surface(
        x=gx, y=gy, z=gz,
        colorscale=[[0, '#0A0C0B'], [1, '#1F2421']],
        showscale=False, opacity=0.5, hoverinfo='none'
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[0, D_cm], y=[0, 0], z=[0, y_ref_end],
        mode='lines+markers',
        name=f"{txt['laser_label']} ({ref_angle_deg:.2f}°)",
        line=dict(color='#8C9490', width=5, dash='dash'),
        marker=dict(size=3, color='#8C9490')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[0, D_cm], y=[0, 0], z=[pos_mira[1], pos_impacto_mira[1]],
        mode='lines+markers',
        name=f"{txt['sight_label']} (α = {angulo_deg:.2f}°)",
        line=dict(color='#F1F3F2', width=7),
        marker=dict(size=4, color='#F1F3F2')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[D_cm], y=[0], z=[y_ref_end],
        mode='markers', name=txt["target_center"],
        marker=dict(size=6, color='#555A57', symbol='circle')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[D_cm], y=[0], z=[y_target_point],
        mode='markers', name=txt["target_point"],
        marker=dict(size=8, color='#FFFFFF', symbol='diamond')
    ))

    fig3d.update_layout(
        title=dict(
            text=f"<b>{txt['title_graph']}</b> | Distancia: {D_val:.1f} {d_unit} | α: {angulo_deg:.4f}°",
            font=dict(color="#F1F3F2", size=13)
        ),
        paper_bgcolor='#121513', plot_bgcolor='#121513',
        height=450, margin=dict(l=5, r=5, t=35, b=5),
        scene=dict(
            aspectmode='manual', aspectratio=dict(x=2.0, y=1, z=1.1),
            xaxis=dict(title='Distancia (cm)', backgroundcolor="#121513", gridcolor="#1F2421", tickfont=dict(color="#8C9490")),
            yaxis=dict(title='Eje Transversal', backgroundcolor="#121513", gridcolor="#1F2421", tickfont=dict(color="#8C9490")),
            zaxis=dict(title='Elevación (cm)', backgroundcolor="#121513", gridcolor="#1F2421", tickfont=dict(color="#8C9490")),
            camera=dict(eye=dict(x=1.6, y=-1.4, z=0.6))
        ),
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(color="#F1F3F2", size=10), bgcolor="rgba(18, 21, 19, 0.9)")
    )
    st.plotly_chart(fig3d, use_container_width=True, key="grafica_optica_3d")

with col_2d:
    fig2d = go.Figure()

    max_radius = max(abs(diferencia_altura_cm) * 1.4, spot_radius_cm * 2.5, 5.0)
    rings = np.linspace(max_radius * 0.2, max_radius, 4)

    for r in reversed(rings):
        fig2d.add_shape(
            type="circle", xref="x", yref="y",
            x0=-r, y0=-r, x1=r, y1=r,
            line=dict(color="#1F2421", width=1),
            fillcolor="rgba(31, 36, 33, 0.15)"
        )

    fig2d.add_shape(type="line", x0=-max_radius*1.2, y0=0, x1=max_radius*1.2, y1=0, line=dict(color="#2D3330", width=1, dash="dot"))
    fig2d.add_shape(type="line", x0=0, y0=-max_radius*1.2, x1=0, y1=max_radius*1.2, line=dict(color="#2D3330", width=1, dash="dot"))

    fig2d.add_shape(
        type="circle", xref="x", yref="y",
        x0=-spot_radius_cm, y0=diferencia_altura_cm - spot_radius_cm,
        x1=spot_radius_cm, y1=diferencia_altura_cm + spot_radius_cm,
        line=dict(color="#F1F3F2", width=1.5),
        fillcolor="rgba(241, 243, 242, 0.2)"
    )

    fig2d.add_trace(go.Scatter(
        x=[0], y=[diferencia_altura_cm],
        mode='markers', name=txt["target_point"],
        marker=dict(size=7, color='#FFFFFF', symbol='cross')
    ))

    fig2d.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers', name=txt["target_center"],
        marker=dict(size=6, color='#8C9490', symbol='circle')
    ))

    fig2d.update_layout(
        title=dict(text=txt["target_2d_title"], font=dict(color="#F1F3F2", size=13)),
        paper_bgcolor='#121513', plot_bgcolor='#121513',
        height=450, margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(range=[-max_radius*1.2, max_radius*1.2], showgrid=False, zeroline=False, tickfont=dict(color="#8C9490"), title=f"X ({h_unit})"),
        yaxis=dict(range=[-max_radius*1.2, max_radius*1.2], showgrid=False, zeroline=False, tickfont=dict(color="#8C9490"), title=f"Y ({h_unit})", scaleanchor="x", scaleratio=1),
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", font=dict(color="#F1F3F2", size=9), bgcolor="rgba(18, 21, 19, 0.9)")
    )
    st.plotly_chart(fig2d, use_container_width=True, key="grafica_diana_2d")

# --- MÉTRICAS DE RESULTADO INSTITUCIONALES ---
st.markdown(f"""
    <div class="metric-card-container">
        <div style="text-align: center; flex: 1;">
            <span style="color: #8C9490; font-size: 11px; font-weight: 500; text-transform: uppercase;">{txt['diff_height']}</span><br>
            <span style="color: #F1F3F2; font-size: 16px; font-weight: 600;">{diff_height_display:.2f} {h_unit}</span>
        </div>
        <div style="text-align: center; border-left: 1px solid #1F2421; padding-left: 10px; flex: 1;">
            <span style="color: #8C9490; font-size: 11px; font-weight: 500; text-transform: uppercase;">{txt['sight_angle']}</span><br>
            <span style="color: #F1F3F2; font-size: 16px; font-weight: 600;">{angulo_deg:.4f}°</span>
        </div>
        <div style="text-align: center; border-left: 1px solid #1F2421; padding-left: 10px; flex: 1.2;">
            <span style="color: #8C9490; font-size: 11px; font-weight: 500; text-transform: uppercase;">{txt['angular_adj']}</span><br>
            <span style="color: #F1F3F2; font-size: 16px; font-weight: 600;">{arcmin:.2f} arcmin | {mrad:.2f} mrad</span>
        </div>
        <div style="text-align: center; border-left: 1px solid #1F2421; padding-left: 10px; flex: 1.2;">
            <span style="color: #8C9490; font-size: 11px; font-weight: 500; text-transform: uppercase;">{txt['spot_size_lbl']}</span><br>
            <span style="color: #F1F3F2; font-size: 16px; font-weight: 600;">Ø {spot_size_display:.2f} {h_unit}</span>
        </div>
        <div style="text-align: center; border-left: 1px solid #1F2421; padding-left: 10px; flex: 1.2;">
            <span style="color: #8C9490; font-size: 11px; font-weight: 500; text-transform: uppercase;">{txt['uncertainty_lbl']}</span><br>
            <span style="color: #F1F3F2; font-size: 15px; font-weight: 600;">{uncertainty_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- HISTORIAL Y EXPORTACIÓN ---
st.markdown("---")
df_db = load_history_from_db()

col_hist_head, col_export, col_hist_btn = st.columns([2.0, 1.2, 1.2])

with col_hist_head:
    st.subheader(txt["history_title"])

with col_export:
    if not df_db.empty:
        csv_data = df_db.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=txt["export_csv"],
            data=csv_data,
            file_name="historial_metrologia_optica.csv",
            mime="text/csv",
            use_container_width=True
        )

with col_hist_btn:
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
    st.dataframe(
        df_db,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Arcmin": st.column_config.NumberColumn("Arcmin", format="%.2f"),
            "mrad": st.column_config.NumberColumn("mrad", format="%.2f"),
        }
    )
else:
    st.info(txt["empty_history"])
