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
    page_title="Centro de Investigaciones en Óptica | Sistema Institucional de Colimación",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# 🔒 MÓDULO DE AUTENTICACIÓN INSTITUCIONAL (NEÓN AVANZADO / CIO LEÓN GTO)
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
    st.error("ACCESO BLOQUEADO. Se ha superado el número máximo de intentos de autenticación institucional.")
    st.stop()

if not st.session_state.autenticado:
    st.markdown("""
        <style>
            header, [data-testid="stHeader"] {
                visibility: hidden;
                height: 0px;
            }
            .stApp {
                background-color: #030504 !important;
                overflow-x: hidden;
            }

            /* Fondo Cyber-Neón Dinámico con Malla Láser */
            .grid-bg {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: 
                    radial-gradient(circle at 50% 50%, rgba(0, 255, 128, 0.08) 0%, rgba(3, 5, 4, 0.98) 100%),
                    linear-gradient(rgba(0, 255, 128, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 255, 128, 0.03) 1px, transparent 1px);
                background-size: 100% 100%, 30px 30px, 30px 30px;
                animation: backgroundShift 25s ease infinite alternate;
                z-index: 0;
                pointer-events: none;
            }

            .top-global-hud {
                position: fixed;
                top: 15px; left: 25px; right: 25px;
                display: flex;
                justify-content: space-between;
                font-family: monospace;
                font-size: 11px;
                color: #00FF80;
                letter-spacing: 2px;
                z-index: 10;
                opacity: 0.95;
                pointer-events: none;
                text-transform: uppercase;
                text-shadow: 0 0 10px rgba(0, 255, 128, 0.6);
            }

            .hud-panel-left, .hud-panel-right {
                position: fixed;
                top: 18vh;
                width: 230px;
                padding: 18px;
                background: rgba(5, 12, 8, 0.9);
                border: 1px solid rgba(0, 255, 128, 0.3);
                backdrop-filter: blur(15px);
                border-radius: 6px;
                font-family: monospace;
                font-size: 10px;
                color: #A3FFD0;
                z-index: 1;
                pointer-events: none;
                box-shadow: 0 0 25px rgba(0, 255, 128, 0.15), inset 0 0 15px rgba(0, 255, 128, 0.05);
            }

            .hud-panel-left { left: 4vw; }
            .hud-panel-right { right: 4vw; }

            .panel-header {
                color: #00FF80;
                font-weight: bold;
                border-bottom: 1px solid rgba(0, 255, 128, 0.4);
                padding-bottom: 6px;
                margin-bottom: 10px;
                letter-spacing: 1.5px;
                text-shadow: 0 0 8px rgba(0, 255, 128, 0.8);
            }

            .hud-data-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
            }

            .login-wrapper {
                position: relative;
                max-width: 480px;
                margin: 5vh auto 0 auto;
                padding: 2px;
                border-radius: 8px;
                background: linear-gradient(135deg, #00FF80, #00B4D8, #030504);
                background-size: 200% 200%;
                animation: borderGlow 6s ease infinite;
                box-shadow: 0 0 40px rgba(0, 255, 128, 0.3), 0 0 80px rgba(0, 180, 216, 0.15);
            }

            .login-card {
                position: relative;
                background: #060A08;
                border-radius: 7px;
                padding: 35px;
                z-index: 2;
            }

            .status-bar-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-family: monospace;
                font-size: 10px;
                color: #00FF80;
                letter-spacing: 1.5px;
                margin-bottom: 15px;
                border-bottom: 1px solid rgba(0, 255, 128, 0.2);
                padding-bottom: 8px;
                text-shadow: 0 0 6px rgba(0, 255, 128, 0.5);
            }

            .loading-bar-container {
                width: 100%;
                height: 3px;
                background: rgba(0, 255, 128, 0.1);
                border-radius: 2px;
                overflow: hidden;
                margin-bottom: 25px;
            }

            .loading-bar-fill {
                width: 40%;
                height: 100%;
                background: linear-gradient(90deg, transparent, #00FF80, #00B4D8, transparent);
                box-shadow: 0 0 10px #00FF80;
                animation: loadingSweep 2s ease-in-out infinite;
            }

            .login-title {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 700;
                text-align: center;
                letter-spacing: 2px;
                text-transform: uppercase;
                margin: 0;
                text-shadow: 0 0 15px rgba(255, 255, 255, 0.6);
            }
            .login-subtitle {
                color: #00FF80;
                font-size: 10px;
                text-align: center;
                letter-spacing: 1.5px;
                opacity: 0.9;
                margin-top: 8px;
                margin-bottom: 25px;
                font-family: monospace;
                text-transform: uppercase;
                text-shadow: 0 0 8px rgba(0, 255, 128, 0.5);
            }

            @keyframes backgroundShift {
                0% { background-position: 0% 0%; }
                100% { background-position: 100% 100%; }
            }

            @keyframes borderGlow {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            @keyframes loadingSweep {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(300%); }
            }

            @media (max-width: 1024px) {
                .hud-panel-left, .hud-panel-right { display: none; }
            }
        </style>

        <div class="grid-bg"></div>

        <div class="top-global-hud">
            <span>INSTITUCIÓN: CIO LEÓN GTO</span>
            <span>MÓDULO: HOLOGRAFÍA & COLIMACIÓN</span>
            <span>ESTADO: SEGURO (NIVEL 4)</span>
        </div>

        <div class="hud-panel-left">
            <div class="panel-header">DIAGNOSTICO_CUÁNTICO</div>
            <div class="hud-data-row"><span>NODO:</span><span style="color:#00FF80">CIO-OPT-01</span></div>
            <div class="hud-data-row"><span>INTERFAZ:</span><span style="color:#00B4D8">ESTABLE</span></div>
            <div class="hud-data-row"><span>LÁSER COHERENTE:</span><span style="color:#00FF80">ACTIVO</span></div>
            <div class="hud-data-row"><span>ANCHO BANDA:</span><span style="color:#00B4D8">10 Gbps</span></div>
        </div>

        <div class="hud-panel-right">
            <div class="panel-header">TELEMETRIA_LOCAL</div>
            <div class="hud-data-row"><span>SERVIDOR:</span><span style="color:#00FF80">LEÓN, GTO</span></div>
            <div class="hud-data-row"><span>LATENCIA:</span><span style="color:#00FF80">2 ms</span></div>
            <div class="hud-data-row"><span>ENCRIPCIÓN:</span><span style="color:#00B4D8">AES-256-NEON</span></div>
            <div class="hud-data-row"><span>ESTADO SSL:</span><span style="color:#00FF80">VERIFICADO</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 1.4, 1])
    
    with col_center:
        st.markdown("""
            <div class="login-wrapper">
                <div class="login-card">
                    <div class="status-bar-top">
                        <span>ACCESO RESTRINGIDO - CIO</span>
                        <span>AUTORIZACIÓN BIOMÉTRICA / TOKEN</span>
                    </div>
                    <div class="loading-bar-container">
                        <div class="loading-bar-fill"></div>
                    </div>
                    <div class="login-title">Centro de Investigaciones en Óptica</div>
                    <div class="login-subtitle">Sistema Institucional de Colimación y Metrología</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("formulario_login"):
            correo = st.text_input("Correo electrónico institucional:", placeholder="usuario@cio.mx")
            password = st.text_input("Contraseña de acceso:", type="password", placeholder="••••••••") 
            boton_ingresar = st.form_submit_button("AUTENTICAR CREDENCIALES", use_container_width=True)
            
            if boton_ingresar:
                correo_ingresado = correo.strip().lower()
                lista_permitidos = [u.strip().lower() for u in USUARIOS_PERMITIDOS]
                
                if correo_ingresado in lista_permitidos and password == CONTRASEÑA_CORRECTA:
                    st.session_state.autenticado = True
                    st.session_state.intentos = 0
                    
                    with st.spinner("Estableciendo enlace de alta fidelidad con servidores del CIO León..."):
                        time.sleep(1.0)
                    st.rerun()
                else:
                    st.session_state.intentos += 1
                    intentos_restantes = MAX_INTENTOS - st.session_state.intentos
                    st.error(f"Credenciales no válidas. Intentos restantes permitidos: {intentos_restantes}")
                    st.stop()

if not st.session_state.autenticado:
    st.stop()

# =========================================================================
# 👇 APLICACIÓN PRINCIPAL (NEÓN MODERNO / CIO LEÓN GTO)
# =========================================================================

DB_NAME = "colimacion_historial.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            perfil TEXT,
            distancia TEXT,
            h_mira TEXT,
            h_extra TEXT,
            spot_size TEXT,
            angulo TEXT,
            moa REAL,
            mrad REAL,
            direccion TEXT,
            clics_moa INTEGER,
            pulsos_mrad INTEGER,
            incertidumbre TEXT,
            param_extra_1 TEXT,
            param_extra_2 TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_record_to_db(rec):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO historial 
        (perfil, distancia, h_mira, h_extra, spot_size, angulo, moa, mrad, direccion, clics_moa, pulsos_mrad, incertidumbre, param_extra_1, param_extra_2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        rec["Línea de Investigación"], rec["Distancia Operativa"], rec["Eje de Colimación"], 
        rec["Desviación del Haz"], rec["Diámetro del Spot"], rec["Ángulo (α)"], 
        rec["MOA"], rec["mrad"], rec["Dirección de Corrección"], rec["Ajuste Clics (1/4 MOA)"], 
        rec["Ajuste Pulsos (0.1 mrad)"], rec["Incertidumbre Metrológica"], rec["ParamExtra1"], rec["ParamExtra2"]
    ))
    conn.commit()
    conn.close()

def load_history_from_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id, fecha AS 'Fecha/Hora', perfil AS 'Línea de Investigación', distancia AS 'Distancia Operativa', h_mira AS 'Eje de Colimación', h_extra AS 'Desviación del Haz', spot_size AS 'Diámetro del Spot', angulo AS 'Ángulo (α)', moa AS 'MOA', mrad AS 'mrad', direccion AS 'Dirección de Corrección', clics_moa AS 'Ajuste Clics (1/4 MOA)', pulsos_mrad AS 'Ajuste Pulsos (0.1 mrad)', incertidumbre AS 'Incertidumbre Metrológica', param_extra_1 AS 'Parámetro Específico A', param_extra_2 AS 'Parámetro Específico B' FROM historial ORDER BY id DESC", conn)
    conn.close()
    return df

def clear_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM historial")
    conn.commit()
    conn.close()

init_db()

# --- ESTILOS CSS PERSONALIZADOS (NEÓN PROFESIONAL / CIO LEÓN GTO) ---
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
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            max-width: 100% !important;
            animation: fadeIn 0.6s ease-out;
        }

        .stApp {
            background-color: #030504 !important;
            color: #E2E8E4 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        [data-testid="stSidebar"] {
            background-color: #060A08 !important;
            border-right: 1px solid rgba(0, 255, 128, 0.2) !important;
            box-shadow: 5px 0 20px rgba(0, 0, 0, 0.8);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.5rem !important;
        }

        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #00FF80 !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 18px !important;
            margin-bottom: 10px !important;
            border-bottom: 1px solid rgba(0, 255, 128, 0.3) !important;
            padding-bottom: 6px;
            text-shadow: 0 0 8px rgba(0, 255, 128, 0.5);
        }

        div.stButton > button {
            background: linear-gradient(135deg, #061A10, #0A2618) !important;
            color: #00FF80 !important;
            border: 1px solid rgba(0, 255, 128, 0.4) !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            font-size: 12px !important;
            letter-spacing: 1px;
            text-transform: uppercase;
            box-shadow: 0 0 10px rgba(0, 255, 128, 0.15);
            transition: all 0.3s ease !important;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #0A2618, #0E3B24) !important;
            color: #FFFFFF !important;
            border-color: #00FF80 !important;
            box-shadow: 0 0 20px rgba(0, 255, 128, 0.5), inset 0 0 10px rgba(0, 255, 128, 0.2);
        }

        button[aria-label="Increase value"], 
        button[aria-label="Decrease value"],
        div[data-baseweb="spinbutton"] button,
        [data-testid="stNumberInputStepDown"],
        [data-testid="stNumberInputStepUp"] {
            color: #00FF80 !important;
            background-color: #060A08 !important;
            border-color: rgba(0, 255, 128, 0.3) !important;
        }

        div[data-baseweb="input"], div[data-baseweb="select"] > div {
            background-color: #060A08 !important;
            border: 1px solid rgba(0, 255, 128, 0.25) !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            box-shadow: inset 0 0 8px rgba(0, 255, 128, 0.05);
        }
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within {
            border-color: #00FF80 !important;
            box-shadow: 0 0 12px rgba(0, 255, 128, 0.4), inset 0 0 8px rgba(0, 255, 128, 0.15);
        }

        .metric-card-container {
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: linear-gradient(135deg, #050E09, #08140E);
            border: 1px solid rgba(0, 255, 128, 0.35); 
            padding: 20px 25px; 
            border-radius: 8px; 
            margin-top: 15px; 
            margin-bottom: 25px;
            box-shadow: 0 0 25px rgba(0, 255, 128, 0.15), inset 0 0 15px rgba(0, 255, 128, 0.05);
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
""", unsafe_allow_html=True)

TEXTS = {
    "ES": {
        "title": "Sistema Institucional de Colimación Óptica y Metrología Láser",
        "lang_select": "Selección de Idioma",
        "unit_select": "Sistema Metrológico de Unidades",
        "metric": "Métrico (cm, metros)",
        "imperial": "Imperial (pulgadas, yardas)",
        "profile_select": "Línea de Investigación e Ingeniería Aplicada",
        "profile_placeholder": "-- Seleccione una Línea de Investigación --",
        "p1": "Interferometría de Alta Resolución y Metrología de Superficies Ópticas",
        "p2": "Caracterización y Alineación de Sistemas Láser Pulsados de Alta Potencia",
        "p3": "Diseño y Fabricación de Componentes Ópticos Difractivos",
        "p4": "Óptica Adaptativa para Corrección de Aberraciones en Telescopios",
        "p5": "Espectroscopía Láser y Análisis de Emisión Atómica",
        "p6": "Metrología Óptica No Destructiva para la Industria Aeroespacial",
        "p7": "Sistemas de Guiado Optoelectrónico y Seguimiento de Alta Precisión",
        "p8": "Control Interferométrico de Vibraciones Mecánicas Estructurales",
        "p9": "Sensores de Fibra Óptica para Monitoreo Geotécnico",
        "p10": "Microscopía Confocal y Óptica de Fluorescencia Avanzada",
        "p11": "Alineación de Arreglos de Espejos Segmentados para Astronomía",
        "p12": "Sistemas LIDAR Terrestres para Modelado Atmosférico",
        "p13": "Óptica Integrada y Circuitos Fotónicos en Silicio",
        "p14": "Caracterización de Materiales Fotónicos y Cristales No Lineales",
        "p15": "Sistemas de Proyección Holográfica y Pantallas Volumétricas",
        "p16": "Instrumentación Óptica para Astrofísica y Observatorios",
        "p17": "Colimadores Láser para Calibración de Sensores Biomecánicos",
        "p18": "Sistemas Ópticos Espaciales y Pruebas de Vacío Térmico",
        "p19": "Procesamiento Óptico de Señales y Computación Fotónica",
        "p20": "Alineación de Cavidades Resonantes en Láseres de Estado Sólido",
        "p21": "Metrología de Frente de Onda en Lámparas Oftálmicas",
        "p22": "Sensores Ópticos Submarinos para Monitoreo Oceanográfico",
        "p23": "Sistemas Ópticos Difractivos para Realidad Mixta",
        "p24": "Litografía Óptica de Submicrométrica Resolución",
        "p25": "Caracterización Termo-Óptica de Polímeros Avanzados",

        "params": "Parámetros Geométricos del Banco Óptico",
        "spec_params": "Parámetros Específicos de la Línea",
        "phys_params": "Parámetros Físicos y Ambientales",
        "reset_btn": "Restablecer Parámetros",
        "save_btn": "Registrar Medición en Base de Datos",
        "export_csv": "Exportar Registros (CSV)",
        "h_mira": "Eje de colimación de referencia",
        "h_extra": "Desviación observada del haz",
        "dist_input": "Distancia operativa al plano focal",
        "ref_angle_input": "Inclinación del eje de referencia (°)",
        "laser_div": "Divergencia del haz láser (mrad)",
        "temp_input": "Temperatura ambiente (°C)",
        "press_input": "Presión atmosférica (hPa)",
        "earth_curv": "Compensación por curvatura de referencia",
        "cm": "cm",
        "m": "m",
        "in": "pulgadas",
        "yd": "yardas",
        "laser_label": "Eje Óptico Base",
        "sight_label": "Eje Ajustado",
        "target_center": "Centro Óptico Teórico",
        "target_point": "Impacto Experimental",
        "title_graph": "Perfil de Propagación Espacial Cuántico-Óptico",
        "req_angle": "Ángulo de Corrección Requerido (α)",
        "diff_height": "Diferencia de Elevación",
        "sight_angle": "Ángulo de Inclinación Óptica (α)",
        "angular_adj": "Corrección Angular",
        "direction": "Dirección de Corrección",
        "direction_up": "Ascendente",
        "direction_down": "Descendente",
        "spot_size_lbl": "Diámetro de Spot (Ø)",
        "curv_drop_lbl": "Compensación Geométrica",
        "uncertainty_lbl": "Incertidumbre Metrológica",
        "history_title": "Historial de Mediciones (Base de Datos Institucional)",
        "clear_history": "Eliminar Base de Datos",
        "confirm_clear_msg": "¿Confirma la eliminación permanente de los registros metrológicos?",
        "confirm_yes": "Confirmar Eliminación",
        "confirm_cancel": "Cancelar Operación",
        "empty_history": "No se encuentran registros almacenados en la base de datos institucional.",
        "select_prompt": "Seleccione una Línea de Investigación e Ingeniería Aplicada en el panel lateral para iniciar la simulación analítica.",
        "record_saved": "Medición registrada permanentemente en el sistema con trazabilidad metrológica.",
        "target_2d_title": "Distribución Transversal del Haz & Dinámica de Campo"
    },
    "EN": {
        "title": "Institutional System for Optical Collimation and Laser Metrology",
        "lang_select": "Language Selection",
        "unit_select": "Metrological Unit System",
        "metric": "Metric (cm, meters)",
        "imperial": "Imperial (inches, yards)",
        "profile_select": "Research Line & Applied Engineering",
        "profile_placeholder": "-- Select a Research Line --",
        "p1": "High-Resolution Interferometry and Optical Surface Metrology",
        "p2": "Characterization and Alignment of High-Power Pulsed Laser Systems",
        "p3": "Design and Fabrication of Diffractive Optical Components",
        "p4": "Adaptive Optics for Aberration Correction in Telescopes",
        "p5": "Laser Spectroscopy and Atomic Emission Analysis",
        "p6": "Non-Destructive Optical Metrology for Aerospace Industry",
        "p7": "Optoelectronic Guidance and High-Precision Tracking Systems",
        "p8": "Interferometric Control of Structural Mechanical Vibrations",
        "p9": "Fiber Optic Sensors for Geotechnical Monitoring",
        "p10": "Confocal Microscopy and Advanced Fluorescence Optics",
        "p11": "Alignment of Segmented Mirror Arrays for Astronomy",
        "p12": "Terrestrial LIDAR Systems for Atmospheric Modeling",
        "p13": "Integrated Optics and Silicon Photonic Circuits",
        "p14": "Characterization of Photonic Materials and Non-Linear Crystals",
        "p15": "Holographic Projection Systems and Volumetric Displays",
        "p16": "Optical Instrumentation for Astrophysics and Observatories",
        "p17": "Laser Collimators for Biomechanical Sensor Calibration",
        "p18": "Space Optical Systems and Thermal Vacuum Testing",
        "p19": "Optical Signal Processing and Photonic Computing",
        "p20": "Alignment of Resonant Cavities in Solid-State Lasers",
        "p21": "Wavefront Metrology in Ophthalmic Instruments",
        "p22": "Submarine Optical Sensors for Oceanographic Monitoring",
        "p23": "Diffractive Optical Systems for Mixed Reality",
        "p24": "Sub-micron Resolution Optical Lithography",
        "p25": "Thermo-Optical Characterization of Advanced Polymers",

        "params": "Optical Bench Geometric Parameters",
        "spec_params": "Line-Specific Parameters",
        "phys_params": "Physical and Environmental Parameters",
        "reset_btn": "Reset Parameters",
        "save_btn": "Record Measurement in Database",
        "export_csv": "Export Records (CSV)",
        "h_mira": "Reference collimation axis",
        "h_extra": "Observed beam deviation",
        "dist_input": "Operating distance to focal plane",
        "ref_angle_input": "Reference axis inclination (°)",
        "laser_div": "Laser beam divergence (mrad)",
        "temp_input": "Ambient temperature (°C)",
        "press_input": "Atmospheric pressure (hPa)",
        "earth_curv": "Reference curvature compensation",
        "cm": "cm",
        "m": "m",
        "in": "inches",
        "yd": "yards",
        "laser_label": "Base Optical Axis",
        "sight_label": "Aligned Axis",
        "target_center": "Theoretical Optical Center",
        "target_point": "Experimental Impact",
        "title_graph": "Spatial Quantum-Optical Propagation Profile",
        "req_angle": "Required Correction Angle (α)",
        "diff_height": "Elevation Difference",
        "sight_angle": "Optical Inclination Angle (α)",
        "angular_adj": "Angular Correction",
        "direction": "Correction Direction",
        "direction_up": "Ascending",
        "direction_down": "Descending",
        "spot_size_lbl": "Spot Diameter (Ø)",
        "curv_drop_lbl": "Geometric Compensation",
        "uncertainty_lbl": "Metrological Uncertainty",
        "history_title": "Measurement History (Institutional Database)",
        "clear_history": "Delete Database",
        "confirm_clear_msg": "Confirm permanent deletion of metrological records?",
        "confirm_yes": "Confirm Deletion",
        "confirm_cancel": "Cancel Operation",
        "empty_history": "No records stored in the institutional database.",
        "select_prompt": "Select a Research Line & Applied Engineering in the sidebar to start analytical simulation.",
        "record_saved": "Measurement permanently recorded in the system with metrological traceability.",
        "target_2d_title": "Transverse Beam Distribution & Field Dynamics"
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

# Variables para parámetros extras por carrera/línea
if "spec_param_1" not in st.session_state: st.session_state["spec_param_1"] = 50.0
if "spec_param_2" not in st.session_state: st.session_state["spec_param_2"] = 1.0

def reset_inputs_to_zero():
    st.session_state["h_mira_val"] = 0.0
    st.session_state["h_extra_val"] = 0.0
    st.session_state["dist_val"] = 0.0
    st.session_state["ref_angle_val"] = 0.0
    st.session_state["laser_div_val"] = 1.0
    st.session_state["spec_param_1"] = 50.0
    st.session_state["spec_param_2"] = 1.0

st.sidebar.header(txt["params"])

if is_metric:
    h_unit, d_unit = txt["cm"], txt["m"]
else:
    h_unit, d_unit = txt["in"], txt["yd"]

H_mira = st.sidebar.number_input(f"{txt['h_mira']} ({h_unit})", min_value=-500.0, max_value=500.0, value=st.session_state["h_mira_val"], step=0.1, key="h_mira_val")
H_extra = st.sidebar.number_input(f"{txt['h_extra']} ({h_unit})", min_value=-500.0, max_value=500.0, value=st.session_state["h_extra_val"], step=0.1, key="h_extra_val")
D_val = st.sidebar.number_input(f"{txt['dist_input']} ({d_unit})", min_value=0.0, max_value=2000.0, value=st.session_state["dist_val"], step=1.0, key="dist_val")
ref_angle_deg = st.sidebar.number_input(txt['ref_angle_input'], min_value=-30.00, max_value=30.00, value=st.session_state["ref_angle_val"], step=0.10, format="%.2f", key="ref_angle_val")

# --- PARÁMETROS EXTRAS DINÁMICOS SEGÚN LA LÍNEA DE INVESTIGACIÓN ---
st.sidebar.header(txt["spec_params"])
spec_label_1, spec_label_2 = "Frecuencia de Modulación (MHz)", "Ganancia Óptica / Coeficiente"

if profile == txt["p1"]: # Interferometría
    spec_label_1, spec_label_2 = "Longitud de Onda (nm)", "Estabilidad de Fase (rad)"
    spec_val_1 = st.sidebar.number_input(spec_label_1, min_value=200.0, max_value=1600.0, value=632.8, step=0.1, key="spec_param_1")
    spec_val_2 = st.sidebar.number_input(spec_label_2, min_value=0.001, max_value=10.0, value=0.05, step=0.001, key="spec_param_2")
elif profile == txt["p2"]: # Láseres Pulsados
    spec_label_1, spec_label_2 = "Energía por Pulso (mJ)", "Tasa de Repetición (kHz)"
    spec_val_1 = st.sidebar.number_input(spec_label_1, min_value=0.1, max_value=5000.0, value=150.0, step=1.0, key="spec_param_1")
    spec_val_2 = st.sidebar.number_input(spec_label_2, min_value=0.01, max_value=1000.0, value=10.0, step=0.1, key="spec_param_2")
elif profile in [txt["p3"], txt["p23"]]: # Óptica Difractiva / Realidad Mixta
    spec_label_1, spec_label_2 = "Eficiencia de Difracción (%)", "Paso de Red (µm)"
    spec_val_1 = st.sidebar.number_input(spec_label_1, min_value=1.0, max_value=100.0, value=88.5, step=0.5, key="spec_param_1")
    spec_val_2 = st.sidebar.number_input(spec_label_2, min_value=0.1, max_value=50.0, value=2.2, step=0.1, key="spec_param_2")
elif profile == txt["p4"]: # Óptica Adaptativa
    spec_label_1, spec_label_2 = "Actuadores del Espejo (n)", "Ancho de Banda Servocontrol (Hz)"
    spec_val_1 = st.sidebar.number_input(spec_label_1, min_value=19.0, max_value=349.0, value=127.0, step=2.0, key="spec_param_1")
    spec_val_2 = st.sidebar.number_input(spec_label_2, min_value=10.0, max_value=5000.0, value=450.0, step=10.0, key="spec_param_2")
else:
    spec_val_1 = st.sidebar.number_input(spec_label_1, min_value=0.0, max_value=10000.0, value=st.session_state["spec_param_1"], step=1.0, key="spec_param_1")
    spec_val_2 = st.sidebar.number_input(spec_label_2, min_value=0.0, max_value=1000.0, value=st.session_state["spec_param_2"], step=0.1, key="spec_param_2")

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

# --- ENCABEZADO INSTITUCIONAL NEÓN ---
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #050E09, #08140E);
                padding: 20px 25px;
                border-radius: 8px;
                border-left: 4px solid #00FF80;
                border-top: 1px solid rgba(0, 255, 128, 0.3);
                border-right: 1px solid rgba(0, 255, 128, 0.3);
                border-bottom: 1px solid rgba(0, 255, 128, 0.3);
                margin-bottom: 25px;
                box-shadow: 0 0 25px rgba(0, 255, 128, 0.15);">
        <h2 style="color: #00FF80; margin: 0; font-size: 20px; font-weight: 700; letter-spacing: 1px; text-shadow: 0 0 10px rgba(0, 255, 128, 0.6);">
            {txt['title']}
        </h2>
        <p style="color: #8FA89B; margin: 6px 0 0 0; font-size: 12px; font-family: monospace;">
            CENTRO DE INVESTIGACIONES EN ÓPTICA, A.C. (LEÓN, GTO.) | LÍNEA ACTIVA: <b style="color: #00FF80; text-shadow: 0 0 6px rgba(0, 255, 128, 0.5);">{profile if profile != txt['profile_placeholder'] else 'Ninguna seleccionada'}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

if profile == txt["profile_placeholder"]:
    st.warning(txt["select_prompt"])
    st.stop()

# --- CÁLCULOS METROLÓGICOS (SciPy y Factores de Carrera) ---
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
# Modulación del spot según el parámetro extra 2 de la carrera
spot_factor = 1.0 + (spec_val_2 * 0.01)
spot_diameter_cm = (0.2 + (2.0 * D_m * math.tan(div_rad / 2.0) * 100.0)) * spot_factor
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
moa, mrad = angulo_deg * 60, angulo_rad * 1000
diff_height_display = diferencia_altura_cm if is_metric else diferencia_altura_cm / 2.54
spot_size_display = spot_diameter_cm if is_metric else spot_diameter_cm / 2.54
curv_drop_display = curv_drop_cm if is_metric else curv_drop_cm / 2.54

delta_h_cm = 0.05
delta_d_cm = 50.0 if D_m > 0 else 0.1
if D_cm > 0:
    sigma_angle_rad = math.sqrt((delta_h_cm / D_cm)**2 + (diferencia_altura_cm * delta_d_cm / (D_cm**2 + diferencia_altura_cm**2))**2)
    confidence_factor = stats.norm.ppf(0.975)
    uncertainty_mrad = sigma_angle_rad * 1000.0 * confidence_factor
    uncertainty_moa = math.degrees(sigma_angle_rad) * 60.0 * confidence_factor
else:
    uncertainty_mrad = 0.0
    uncertainty_moa = 0.0

uncertainty_str = f"±{uncertainty_mrad:.2f} mrad (95% IC)"

is_up = (angulo_deg >= 0)
direccion_str = txt["direction_up"] if is_up else txt["direction_down"]

clicks_moa = abs(round(moa * 4))
pulsos_mrad = abs(round(mrad * 10))

if save_clicked:
    current_record = {
        "Línea de Investigación": profile,
        "Distancia Operativa": f"{D_val:.1f} {d_unit}",
        "Eje de Colimación": f"{H_mira:.2f} {h_unit}",
        "Desviación del Haz": f"{H_extra:.2f} {h_unit}",
        "Diámetro del Spot": f"{spot_size_display:.2f} {h_unit}",
        "Ángulo (α)": f"{angulo_deg:.4f}°",
        "MOA": moa,
        "mrad": mrad,
        "Dirección de Corrección": direccion_str,
        "Ajuste Clics (1/4 MOA)": clicks_moa,
        "Ajuste Pulsos (0.1 mrad)": pulsos_mrad,
        "Incertidumbre Metrológica": uncertainty_str,
        "ParamExtra1": f"{spec_val_1:.2f}",
        "ParamExtra2": f"{spec_val_2:.2f}"
    }
    save_record_to_db(current_record)
    st.sidebar.success(txt["record_saved"])

# --- VISUALIZACIONES GRÁFICAS NEÓN ADAPTADAS A PARÁMETROS DE CARRERA ---
col_3d, col_2d = st.columns([1.75, 1.0])

with col_3d:
    pos_mira = (0, H_mira_cm)
    pos_impacto_mira = (D_cm, y_target_point)

    fig3d = go.Figure()

    grid_x = np.linspace(0, max(D_cm, 10), 12)
    grid_y = np.linspace(-max(abs(H_extra_cm)*1.5, 20), max(abs(H_extra_cm)*1.5, 20), 12)
    gx, gy = np.meshgrid(grid_x, grid_y)
    gz = np.zeros_like(gx)

    # Superficie con tintes neón oscuros
    fig3d.add_trace(go.Surface(
        x=gx, y=gy, z=gz,
        colorscale=[[0, '#030504'], [1, '#081C12']],
        showscale=False, opacity=0.6, hoverinfo='none'
    ))

    # Eje láser base con brillo cian/verde
    fig3d.add_trace(go.Scatter3d(
        x=[0, D_cm], y=[0, 0], z=[0, y_ref_end],
        mode='lines+markers',
        name=f"{txt['laser_label']} ({ref_angle_deg:.2f}°)",
        line=dict(color='#00B4D8', width=5, dash='dash'),
        marker=dict(size=3, color='#00B4D8')
    ))

    # Eje ajustado con brillo verde neón intenso
    fig3d.add_trace(go.Scatter3d(
        x=[0, D_cm], y=[0, 0], z=[pos_mira[1], pos_impacto_mira[1]],
        mode='lines+markers',
        name=f"{txt['sight_label']} (α = {angulo_deg:.2f}°)",
        line=dict(color='#00FF80', width=7),
        marker=dict(size=4, color='#00FF80')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[D_cm], y=[0], z=[y_ref_end],
        mode='markers', name=txt["target_center"],
        marker=dict(size=6, color='#00B4D8', symbol='circle')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[D_cm], y=[0], z=[y_target_point],
        mode='markers', name=txt["target_point"],
        marker=dict(size=8, color='#00FF80', symbol='diamond')
    ))

    fig3d.update_layout(
        title=dict(
            text=f"<b>{txt['title_graph']}</b><br><span style='font-size:10px; color:#00FF80;'>Parámetro Específico 1: {spec_val_1:.2f} | Parámetro Específico 2: {spec_val_2:.2f}</span>",
            font=dict(color="#00FF80", size=13)
        ),
        paper_bgcolor='#060A08', plot_bgcolor='#060A08',
        height=460, margin=dict(l=5, r=5, t=45, b=5),
        scene=dict(
            aspectmode='manual', aspectratio=dict(x=2.0, y=1, z=1.1),
            xaxis=dict(title='Distancia (cm)', backgroundcolor="#060A08", gridcolor="#0A2618", tickfont=dict(color="#00FF80")),
            yaxis=dict(title='Eje Transversal', backgroundcolor="#060A08", gridcolor="#0A2618", tickfont=dict(color="#00FF80")),
            zaxis=dict(title='Elevación (cm)', backgroundcolor="#060A08", gridcolor="#0A2618", tickfont=dict(color="#00FF80")),
            camera=dict(eye=dict(x=1.6, y=-1.4, z=0.6))
        ),
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(color="#E2E8E4", size=9), bgcolor="rgba(6, 10, 8, 0.95)")
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
            line=dict(color="#0A2618", width=1.5),
            fillcolor="rgba(0, 255, 128, 0.03)"
        )

    fig2d.add_shape(type="line", x0=-max_radius*1.2, y0=0, x1=max_radius*1.2, y1=0, line=dict(color="#0E3B24", width=1, dash="dot"))
    fig2d.add_shape(type="line", x0=0, y0=-max_radius*1.2, x1=0, y1=max_radius*1.2, line=dict(color="#0E3B24", width=1, dash="dot"))

    # Spot beam con efecto neón brillante
    fig2d.add_shape(
        type="circle", xref="x", yref="y",
        x0=-spot_radius_cm, y0=diferencia_altura_cm - spot_radius_cm,
        x1=spot_radius_cm, y1=diferencia_altura_cm + spot_radius_cm,
        line=dict(color="#00FF80", width=2),
        fillcolor="rgba(0, 255, 128, 0.2)"
    )

    fig2d.add_trace(go.Scatter(
        x=[0], y=[diferencia_altura_cm],
        mode='markers', name=txt["target_point"],
        marker=dict(size=8, color='#00FF80', symbol='cross', line=dict(width=1, color='#FFFFFF'))
    ))

    fig2d.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers', name=txt["target_center"],
        marker=dict(size=6, color='#00B4D8', symbol='circle')
    ))

    fig2d.update_layout(
        title=dict(text=txt["target_2d_title"], font=dict(color="#00FF80", size=13)),
        paper_bgcolor='#060A08', plot_bgcolor='#060A08',
        height=460, margin=dict(l=10, r=10, t=45, b=10),
        xaxis=dict(range=[-max_radius*1.2, max_radius*1.2], showgrid=False, zeroline=False, tickfont=dict(color="#00FF80"), title=f"X ({h_unit})"),
        yaxis=dict(range=[-max_radius*1.2, max_radius*1.2], showgrid=False, zeroline=False, tickfont=dict(color="#00FF80"), title=f"Y ({h_unit})", scaleanchor="x", scaleratio=1),
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", font=dict(color="#E2E8E4", size=9), bgcolor="rgba(6, 10, 8, 0.95)")
    )
    st.plotly_chart(fig2d, use_container_width=True, key="grafica_diana_2d")

# --- TARJETA DE MÉTRICAS INSTITUCIONALES NEÓN ---
st.markdown(f"""
    <div class="metric-card-container">
        <div style="text-align: center; flex: 1;">
            <span style="color: #00FF80; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 5px rgba(0,255,128,0.5);">{txt['diff_height']}</span><br>
            <span style="color: #FFFFFF; font-size: 16px; font-weight: 700; text-shadow: 0 0 10px rgba(255,255,255,0.4);">{diff_height_display:.2f} {h_unit}</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 255, 128, 0.2); padding-left: 10px; flex: 1;">
            <span style="color: #00FF80; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 5px rgba(0,255,128,0.5);">{txt['sight_angle']}</span><br>
            <span style="color: #FFFFFF; font-size: 16px; font-weight: 700; text-shadow: 0 0 10px rgba(255,255,255,0.4);">{angulo_deg:.4f}°</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 255, 128, 0.2); padding-left: 10px; flex: 1.2;">
            <span style="color: #00FF80; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 5px rgba(0,255,128,0.5);">{txt['angular_adj']}</span><br>
            <span style="color: #FFFFFF; font-size: 16px; font-weight: 700; text-shadow: 0 0 10px rgba(255,255,255,0.4);">{moa:.2f} MOA | {mrad:.2f} mrad</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 255, 128, 0.2); padding-left: 10px; flex: 1.2;">
            <span style="color: #00FF80; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 5px rgba(0,255,128,0.5);">{txt['spot_size_lbl']}</span><br>
            <span style="color: #FFFFFF; font-size: 16px; font-weight: 700; text-shadow: 0 0 10px rgba(255,255,255,0.4);">Ø {spot_size_display:.2f} {h_unit}</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 255, 128, 0.2); padding-left: 10px; flex: 1.2;">
            <span style="color: #00FF80; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 5px rgba(0,255,128,0.5);">{txt['uncertainty_lbl']}</span><br>
            <span style="color: #00B4D8; font-size: 14px; font-weight: 700; text-shadow: 0 0 8px rgba(0,180,216,0.6);">{uncertainty_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE BASE DE DATOS Y EXPORTACIÓN ---
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
            file_name="historial_colimacion_cio_neon.csv",
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
            "MOA": st.column_config.NumberColumn("MOA", format="%.2f"),
            "mrad": st.column_config.NumberColumn("mrad", format="%.2f"),
        }
    )
else:
    st.info(txt["empty_history"])
