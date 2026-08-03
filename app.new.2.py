import streamlit as st
import numpy as np
import math
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import time
from scipy import stats

# 1. Configuración de la página (¡SIEMPRE PRIMERO EN STREAMLIT!)
st.set_page_config(
    page_title="Simulador de Metrología y Alineación Optomecánica - CIO",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================================
# 🔒 MÓDULO DE SEGURIDAD CON MARCO HUD MONOCROMÁTICO NEÓN Y FONDO ANIMADO
# =========================================================================

USUARIOS_PERMITIDOS = [
    "j3remyx1010@gmail.com",
    "correo2@ejemplo.com"
]

CONTRASEÑA_CORRECTA = "Jggg101031"
MAX_INTENTOS = 3

# Inicializar variables de estado seguro
if "intentos" not in st.session_state:
    st.session_state.intentos = 0
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Bloqueo total por seguridad
if st.session_state.intentos >= MAX_INTENTOS:
    st.error("❌ Demasiados intentos fallidos. Acceso bloqueado temporalmente.")
    st.stop()

# Interfaz de Inicio de Sesión
if not st.session_state.autenticado:
    st.markdown("""
        <style>
            /* Ocultar barra superior e interfaz de fondo Streamlit */
            header, [data-testid="stHeader"] {
                visibility: hidden;
                height: 0px;
            }
            .stApp {
                background-color: #02040a !important;
                overflow-x: hidden;
            }

            /* Fondo Avanzado con Malla Sci-Fi Animada y Fluida */
            .grid-bg {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: 
                    linear-gradient(rgba(0, 240, 255, 0.12) 1.5px, transparent 1.5px),
                    linear-gradient(90deg, rgba(0, 240, 255, 0.05) 1.5px, transparent 1.5px);
                background-size: 40px 40px, 40px 40px;
                animation: gridMove 18s linear infinite;
                z-index: 0;
                pointer-events: none;
            }

            @keyframes gridMove {
                0% { background-position: 0 0, 0 0; }
                100% { background-position: 40px 40px, 40px 40px; }
            }

            /* Indicadores Globales de la Interfaz en Esquinas Superiores */
            .top-global-hud {
                position: fixed;
                top: 15px; left: 25px; right: 25px;
                display: flex;
                justify-content: space-between;
                font-family: monospace;
                font-size: 11px;
                color: #00f0ff;
                letter-spacing: 1.5px;
                z-index: 10;
                opacity: 0.95;
                pointer-events: none;
                text-shadow: 0 0 12px rgba(0, 240, 255, 0.85);
            }

            /* Módulos Flotantes Periféricos */
            .hud-panel-left, .hud-panel-right {
                position: fixed;
                top: 18vh;
                width: 220px;
                padding: 16px;
                background: rgba(3, 8, 20, 0.7);
                border: 1px solid rgba(0, 240, 255, 0.35);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                font-family: monospace;
                font-size: 10px;
                color: #a5f3fc;
                z-index: 1;
                pointer-events: none;
                box-shadow: 0 0 15px rgba(0, 240, 255, 0.1);
                animation: sidePanelEntrance 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }

            .hud-panel-left { left: 4vw; }
            .hud-panel-right { right: 4vw; }

            .panel-header {
                color: #00f0ff;
                font-weight: bold;
                border-bottom: 1px dashed rgba(0, 240, 255, 0.5);
                padding-bottom: 4px;
                margin-bottom: 10px;
                letter-spacing: 1px;
                text-shadow: 0 0 8px rgba(0, 240, 255, 0.7);
            }

            .hud-data-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 6px;
            }

            /* Contenedor Exterior con Borde Monocromático Neón Sólido */
            .login-wrapper {
                position: relative;
                max-width: 460px;
                margin: 4vh auto 0 auto;
                padding: 2px;
                border-radius: 20px;
                background: linear-gradient(135deg, #00f0ff, #0077ff, #00f0ff);
                background-size: 200% 200%;
                animation: borderGlow 4s ease infinite, entranceZoom 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                box-shadow: 0 0 30px rgba(0, 240, 255, 0.35);
            }

            /* Aureola Fina Giratoria Exterior única (Simplificada) */
            .aureola-halo {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 520px;
                height: 520px;
                transform: translate(-50%, -50%);
                border: 1.5px dashed rgba(0, 240, 255, 0.7);
                border-radius: 50%;
                animation: haloRotate 25s linear infinite;
                pointer-events: none;
                z-index: 0;
                box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
            }

            /* Tarjeta Interior de Login con Glassmorphism Monocromático */
            .login-card {
                position: relative;
                background: rgba(4, 7, 17, 0.96);
                backdrop-filter: blur(16px);
                border-radius: 18px;
                padding: 25px 25px 15px 25px;
                z-index: 2;
            }

            /* Barra de Telemetría Superior */
            .status-bar-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-family: monospace;
                font-size: 10px;
                color: #00f0ff;
                letter-spacing: 1px;
                margin-bottom: 12px;
                border-bottom: 1px solid rgba(0, 240, 255, 0.3);
                padding-bottom: 6px;
                text-shadow: 0 0 6px rgba(0, 240, 255, 0.5);
            }

            .loading-bar-container {
                width: 100%;
                height: 3px;
                background: rgba(0, 240, 255, 0.15);
                border-radius: 2px;
                overflow: hidden;
                margin-bottom: 15px;
            }

            .loading-bar-fill {
                width: 40%;
                height: 100%;
                background: linear-gradient(90deg, transparent, #00f0ff, transparent);
                box-shadow: 0 0 8px #00f0ff;
                animation: loadingSweep 1.8s ease-in-out infinite;
            }

            /* Contenedor HUD Central Simplificado (Sin exceso de animaciones) */
            .hud-box {
                position: relative;
                width: 120px;
                height: 120px;
                margin: 0 auto 12px auto;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }

            /* Esquinas HUD Estáticas/Limpias */
            .corner {
                position: absolute;
                width: 18px;
                height: 18px;
                border-color: #00f0ff;
                border-style: solid;
                z-index: 2;
            }
            .top-left { top: 2px; left: 2px; border-width: 2px 0 0 2px; }
            .top-right { top: 2px; right: 2px; border-width: 2px 2px 0 0; }
            .bottom-left { bottom: 2px; left: 2px; border-width: 0 0 2px 2px; }
            .bottom-right { bottom: 2px; right: 2px; border-width: 0 2px 2px 0; }

            /* Único Anillo Giratorio Interno */
            .hud-ring-outer {
                position: absolute;
                width: 85px;
                height: 85px;
                border: 1px dashed rgba(0, 240, 255, 0.6);
                border-radius: 50%;
                animation: rotateRight 12s linear infinite;
            }

            /* Retícula Crosshair */
            .hud-cross-h { position: absolute; width: 75px; height: 1px; background: rgba(0, 240, 255, 0.5); }
            .hud-cross-v { position: absolute; width: 1px; height: 75px; background: rgba(0, 240, 255, 0.5); }

            /* Punto Láser Central Cian Neón */
            .hud-dot {
                position: absolute;
                width: 6px;
                height: 6px;
                background-color: #00f0ff;
                border-radius: 50%;
                box-shadow: 0 0 12px #00f0ff;
                z-index: 3;
            }

            /* Scanline Vertical Suave */
            .hud-scanline {
                position: absolute;
                top: -100%;
                left: 0;
                width: 100%;
                height: 30%;
                background: linear-gradient(180deg, rgba(0, 240, 255, 0) 0%, rgba(0, 240, 255, 0.4) 100%);
                animation: scanMove 3s infinite ease-in-out;
                z-index: 1;
            }

            /* Títulos del Formulario */
            .login-title {
                color: #ffffff;
                font-size: 17px;
                font-weight: 700;
                text-align: center;
                letter-spacing: 1px;
                text-transform: uppercase;
                margin: 0;
                text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
            }
            .login-subtitle {
                color: #00f0ff;
                font-size: 10px;
                text-align: center;
                letter-spacing: 0.5px;
                opacity: 0.9;
                margin-top: 4px;
                margin-bottom: 12px;
                font-family: monospace;
            }

            div[data-baseweb="input"] input:focus {
                border-color: #00f0ff !important;
                box-shadow: 0 0 15px rgba(0, 240, 255, 0.7) !important;
            }

            @keyframes haloRotate {
                from { transform: translate(-50%, -50%) rotate(0deg); }
                to { transform: translate(-50%, -50%) rotate(360deg); }
            }

            @keyframes entranceZoom {
                0% { opacity: 0; transform: scale(0.94) translateY(-15px); }
                100% { opacity: 1; transform: scale(1) translateY(0); }
            }

            @keyframes sidePanelEntrance {
                0% { opacity: 0; transform: translateY(20px); }
                100% { opacity: 1; transform: translateY(0); }
            }

            @keyframes borderGlow {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            @keyframes loadingSweep {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(250%); }
            }

            @keyframes rotateRight {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            @keyframes scanMove {
                0% { top: -40%; }
                50% { top: 100%; }
                100% { top: -40%; }
            }

            @media (max-width: 1024px) {
                .hud-panel-left, .hud-panel-right, .aureola-halo { display: none; }
            }
        </style>

        <div class="grid-bg"></div>

        <div class="top-global-hud">
            <span>● SYSTEM: ONLINE</span>
            <span>ENCRYPTION: AES-256</span>
            <span>NODE: CIO-OPTICS-LAB</span>
        </div>

        <div class="hud-panel-left">
            <div class="panel-header">DIAGNOSTICO_LAB</div>
            <div class="hud-data-row"><span>INTERFEROMETRO:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">ESTABLE</span></div>
            <div class="hud-data-row"><span>SENSORES PSD:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">CALIBRADOS</span></div>
            <div class="hud-data-row"><span>HAZ LASER:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">TEM00</span></div>
            <div class="hud-data-row"><span>METROLOGÍA:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">ACTIVA</span></div>
        </div>

        <div class="hud-panel-right">
            <div class="panel-header">TELEMETRIA_SISTEMA</div>
            <div class="hud-data-row"><span>ESTACIÓN:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">CIO-LEÓN</span></div>
            <div class="hud-data-row"><span>ADQUISICIÓN:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">100 kS/s</span></div>
            <div class="hud-data-row"><span>BANCADA:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">OPTOMECÁNICA</span></div>
            <div class="hud-data-row"><span>ESTABILIDAD:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">λ/10</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 1.3, 1])
    
    with col_center:
        st.markdown("""
            <div class="login-wrapper">
                <div class="aureola-halo"></div>
                <div class="login-card">
                    <div class="status-bar-top">
                        <span>SYS.STATUS: ONLINE</span>
                        <span>LINK: 100% SECURE</span>
                    </div>
                    <div class="loading-bar-container">
                        <div class="loading-bar-fill"></div>
                    </div>
                    <div class="hud-box">
                        <div class="corner top-left"></div>
                        <div class="corner top-right"></div>
                        <div class="corner bottom-left"></div>
                        <div class="corner bottom-right"></div>
                        <div class="hud-cross-h"></div>
                        <div class="hud-cross-v"></div>
                        <div class="hud-ring-outer"></div>
                        <div class="hud-dot"></div>
                        <div class="hud-scanline"></div>
                    </div>
                    <div class="login-title">Autenticación Espectral</div>
                    <div class="login-subtitle">● SISTEMA DE METROLOGÍA Y ALINEACIÓN ÓPTICA</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("formulario_login"):
            correo = st.text_input("✉️ Correo electrónico autorizado:", placeholder="ejemplo@correo.com")
            password = st.text_input("🔑 Contraseña:", type="password", placeholder="••••••••") 
            boton_ingresar = st.form_submit_button("Acceder al Sistema", use_container_width=True)
            
            if boton_ingresar:
                correo_ingresado = correo.strip().lower()
                lista_permitidos = [u.strip().lower() for u in USUARIOS_PERMITIDOS]
                
                if correo_ingresado in lista_permitidos and password == CONTRASEÑA_CORRECTA:
                    st.session_state.autenticado = True
                    st.session_state.intentos = 0
                    
                    with st.spinner("🔍 Analizando matriz y calibrando transductores..."):
                        time.sleep(0.8)
                    st.rerun()
                else:
                    st.session_state.intentos += 1
                    intentos_restantes = MAX_INTENTOS - st.session_state.intentos
                    st.error(f"Credenciales incorrectas. Intentos restantes: {intentos_restantes}")
                    st.stop()

if not st.session_state.autenticado:
    st.stop()


# =========================================================================
# 👇 CÓDIGO DEL SIMULADOR DE METROLOGÍA ÓPTICA (ESTÉTICA MONOCROMÁTICA NEÓN)
# =========================================================================

# --- BASE DE DATOS SQLITE ---
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

# Inicializar Base de Datos
init_db()

# --- ESTILOS CSS PERSONALIZADOS (MONOCROMÁTICO NEÓN CIAN & SLIM LAYOUT) ---
st.markdown("""
    <style>
        header, [data-testid="stHeader"], [data-testid="stToolbar"] {
            visibility: hidden !important;
            height: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
        }

        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
            animation: fadeIn 0.5s ease-out;
        }

        .stApp {
            background-color: #02040a !important;
            color: #e0f2fe !important;
        }

        /* Estilo de la Barra Lateral */
        [data-testid="stSidebar"] {
            background-color: #040816 !important;
            border-right: 1px solid rgba(0, 240, 255, 0.2) !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.5rem !important;
        }

        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #00f0ff !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 15px !important;
            margin-bottom: 10px !important;
            border-bottom: 1px solid rgba(0, 240, 255, 0.2) !important;
            padding-bottom: 4px;
            text-shadow: 0 0 6px rgba(0, 240, 255, 0.4);
        }

        /* Botones Interactivos Monocromáticos */
        div.stButton > button {
            background: linear-gradient(135deg, #050d21 0%, #081b3a 100%) !important;
            color: #00f0ff !important;
            border: 1px solid rgba(0, 240, 255, 0.35) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 0 8px rgba(0, 240, 255, 0.1);
        }
        div.stButton > button:hover {
            background: #00f0ff !important;
            color: #02040a !important;
            box-shadow: 0px 0px 15px rgba(0, 240, 255, 0.6) !important;
            border-color: #00f0ff !important;
            transform: translateY(-1px);
        }

        button[aria-label="Increase value"], 
        button[aria-label="Decrease value"],
        div[data-baseweb="spinbutton"] button,
        [data-testid="stNumberInputStepDown"],
        [data-testid="stNumberInputStepUp"] {
            color: #00f0ff !important;
            background-color: #050d21 !important;
            border-color: rgba(0, 240, 255, 0.3) !important;
        }

        button[aria-label="Increase value"]:hover, 
        button[aria-label="Decrease value"]:hover,
        div[data-baseweb="spinbutton"] button:hover,
        [data-testid="stNumberInputStepDown"]:hover,
        [data-testid="stNumberInputStepUp"]:hover {
            background-color: #00f0ff !important;
            color: #02040a !important;
            box-shadow: 0px 0px 10px rgba(0, 240, 255, 0.5) !important;
        }

        div[data-baseweb="input"], div[data-baseweb="select"] > div {
            background-color: #050d21 !important;
            border: 1px solid rgba(0, 240, 255, 0.25) !important;
            color: #ffffff !important;
            border-radius: 6px !important;
        }

        div[data-baseweb="input"]:hover, div[data-baseweb="select"] > div:hover {
            border-color: rgba(0, 240, 255, 0.6) !important;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.2) !important;
        }

        /* Tarjetas de Métricas Neón Cian */
        .metric-card-container {
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: linear-gradient(135deg, #040816 0%, #061028 100%);
            border: 1px solid rgba(0, 240, 255, 0.3); 
            padding: 16px 20px; 
            border-radius: 12px; 
            margin-top: 15px; 
            margin-bottom: 25px;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.12);
        }

        div.btn-confirm-yes > div.stButton > button {
            background: linear-gradient(135deg, #022c22 0%, #065f46 100%) !important;
            color: #34d399 !important;
            border: 1px solid #065f46 !important;
        }
        div.btn-confirm-yes > div.stButton > button:hover {
            background: #34d399 !important;
            color: #000000 !important;
            box-shadow: 0px 0px 12px rgba(52, 211, 153, 0.5);
        }

        div.btn-confirm-cancel > div.stButton > button {
            background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%) !important;
            color: #f87171 !important;
            border: 1px solid #7f1d1d !important;
        }
        div.btn-confirm-cancel > div.stButton > button:hover {
            background: #f87171 !important;
            color: #000000 !important;
            box-shadow: 0px 0px 12px rgba(248, 113, 113, 0.5);
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

# --- DICCIONARIOS DE TRADUCCIÓN ---
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
        "cm": "cm",
        "m": "m",
        "in": "pulgadas",
        "yd": "yardas",
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
        "cm": "cm",
        "m": "m",
        "in": "inches",
        "yd": "yards",
        "laser_label": "Theoretical Optical Axis",
        "sight_label": "Aligned Beam Axis",
        "target_center": "PSD Sensor Center",
        "target_point": "Laser Beam Centroid",
        "title_graph": "Propagation",
        "req_angle": "Correction Angle (α)",
        "diff_height": "Total Linear Deviation",
        "sight_angle": "Beam Inclination Angle (α)",
        "angular_adj": "Angular Adjustment (Resolution)",
        "direction": "Correction Sense",
        "direction_up": "Ascending (+Z)",
        "direction_down": "Descending (-Z)",
        "spot_size_lbl": "Beam Waist Diameter (1/e²)",
        "curv_drop_lbl": "Atmospheric Correction",
        "uncertainty_lbl": "Expanded Uncertainty (SciPy)",
        "history_title": "Metrological Database Records (SQLite)",
        "clear_history": "Clear Database",
        "confirm_clear_msg": "Are you sure you want to clear the metrological registry?",
        "confirm_yes": "✔ Yes, Clear",
        "confirm_cancel": "✖ Cancel",
        "empty_history": "No experimental records saved in database yet.",
        "select_prompt": "⚠️ Please select an Experimental Setup / Optical Bench in the sidebar to start the metrological simulation.",
        "record_saved": "✅ Metrological measurement recorded permanently into SQLite.",
        "target_2d_title": "🎯 Transverse 2D Profile (PSD Sensor / Profilometer)"
    }
}

# --- SELECCIÓN DE IDIOMA ---
st.sidebar.header("Configuración / Settings")
lang = st.sidebar.selectbox("Idioma / Language", ["Español", "English"])
lang_code = "ES" if lang == "Español" else "EN"
txt = TEXTS[lang_code]

# --- MENÚ DESPLEGABLE DE CONFIGURACIONES EXPERIMENTALES ---
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

# --- ENCABEZADO PRINCIPAL NEÓN CIAN ---
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #040816 0%, #071530 100%);
                padding: 14px 25px;
                border-radius: 12px;
                border-left: 5px solid #00f0ff;
                border: 1px solid rgba(0, 240, 255, 0.25);
                margin-bottom: 20px;
                box-shadow: 0px 4px 15px rgba(0, 240, 255, 0.1);">
        <h2 style="color: #ffffff; margin: 0; font-size: 24px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; letter-spacing: 1px; text-shadow: 0 0 8px rgba(0,240,255,0.4);">
            {txt['title']}
        </h2>
        <p style="color: #93c5fd; margin: 0; font-size: 13px; opacity: 0.9;">
            Centro de Investigaciones en Óptica (CIO) | Configuración Activa: <b style="color: #00f0ff;">{profile if profile != txt['profile_placeholder'] else 'Ninguna'}</b>
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

# --- REGISTRO A BASE DE DATOS EN SQLite ---
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

# --- GRÁFICAS 3D Y 2D OPTIMIZADAS PARA RÁPIDA RENDERIZACIÓN ---
col_3d, col_2d = st.columns([1.75, 1.0])

with col_3d:
    pos_mira = (0, H_mira_cm)
    pos_impacto_mira = (D_cm, y_target_point)

    fig3d = go.Figure()

    grid_x = np.linspace(0, max(D_cm, 10), 8)
    grid_y = np.linspace(-max(abs(H_extra_cm)*1.5, 20), max(abs(H_extra_cm)*1.5, 20), 8)
    gx, gy = np.meshgrid(grid_x, grid_y)
    gz = np.zeros_like(gx)

    fig3d.add_trace(go.Surface(
        x=gx, y=gy, z=gz,
        colorscale=[[0, '#02040a'], [1, '#071530']],
        showscale=False, opacity=0.5, hoverinfo='none'
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[0, D_cm], y=[0, 0], z=[0, y_ref_end],
        mode='lines+markers',
        name=f"{txt['laser_label']} ({ref_angle_deg:.2f}°)",
        line=dict(color='#38bdf8', width=6, dash='dash'),
        marker=dict(size=3, color='#38bdf8')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[0, D_cm], y=[0, 0], z=[pos_mira[1], pos_impacto_mira[1]],
        mode='lines+markers',
        name=f"{txt['sight_label']} (α = {angulo_deg:.2f}°)",
        line=dict(color='#00f0ff', width=8),
        marker=dict(size=4, color='#00f0ff')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[D_cm], y=[0], z=[y_ref_end],
        mode='markers', name=txt["target_center"],
        marker=dict(size=7, color='#38ef7d', symbol='circle')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[D_cm], y=[0], z=[y_target_point],
        mode='markers', name=txt["target_point"],
        marker=dict(size=9, color='#00f0ff', symbol='diamond')
    ))

    fig3d.update_layout(
        title=dict(
            text=f"📐 <b>{txt['title_graph']} 3D</b>: {D_val:.1f} {d_unit} | <b>α</b>: {angulo_deg:.4f}°",
            font=dict(color="#00f0ff", size=14)
        ),
        paper_bgcolor='#030712', plot_bgcolor='#030712',
        height=450, margin=dict(l=5, r=5, t=35, b=5),
        scene=dict(
            aspectmode='manual', aspectratio=dict(x=2.0, y=1, z=1.1),
            xaxis=dict(title='Distancia (cm)', backgroundcolor="#030712", gridcolor="#0f2147", tickfont=dict(color="#93c5fd")),
            yaxis=dict(title='Eje Transversal', backgroundcolor="#030712", gridcolor="#0f2147", tickfont=dict(color="#93c5fd")),
            zaxis=dict(title='Elevación (cm)', backgroundcolor="#030712", gridcolor="#0f2147", tickfont=dict(color="#93c5fd")),
            camera=dict(eye=dict(x=1.6, y=-1.4, z=0.6))
        ),
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(color="white", size=10), bgcolor="rgba(4, 8, 22, 0.9)")
    )
    st.plotly_chart(fig3d, use_container_width=True, key="grafica_optica_3d", config={"displayModeBar": False})

with col_2d:
    fig2d = go.Figure()

    max_radius = max(abs(diferencia_altura_cm) * 1.4, spot_radius_cm * 2.5, 5.0)
    rings = np.linspace(max_radius * 0.2, max_radius, 3)

    for r in reversed(rings):
        fig2d.add_shape(
            type="circle", xref="x", yref="y",
            x0=-r, y0=-r, x1=r, y1=r,
            line=dict(color="#0e294b", width=1.2),
            fillcolor="rgba(14, 41, 75, 0.15)"
        )

    fig2d.add_shape(type="line", x0=-max_radius*1.2, y0=0, x1=max_radius*1.2, y1=0, line=dict(color="#1e3a8a", width=1, dash="dot"))
    fig2d.add_shape(type="line", x0=0, y0=-max_radius*1.2, x1=0, y1=max_radius*1.2, line=dict(color="#1e3a8a", width=1, dash="dot"))

    fig2d.add_shape(
        type="circle", xref="x", yref="y",
        x0=-spot_radius_cm, y0=diferencia_altura_cm - spot_radius_cm,
        x1=spot_radius_cm, y1=diferencia_altura_cm + spot_radius_cm,
        line=dict(color="#00f0ff", width=2),
        fillcolor="rgba(0, 240, 255, 0.25)"
    )

    fig2d.add_trace(go.Scatter(
        x=[0], y=[diferencia_altura_cm],
        mode='markers', name=txt["target_point"],
        marker=dict(size=8, color='#00f0ff', symbol='cross')
    ))

    fig2d.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers', name=txt["target_center"],
        marker=dict(size=7, color='#38ef7d', symbol='circle')
    ))

    fig2d.update_layout(
        title=dict(text=txt["target_2d_title"], font=dict(color="#00f0ff", size=14)),
        paper_bgcolor='#030712', plot_bgcolor='#030712',
        height=450, margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(range=[-max_radius*1.2, max_radius*1.2], showgrid=False, zeroline=False, tickfont=dict(color="#93c5fd"), title=f"X ({h_unit})"),
        yaxis=dict(range=[-max_radius*1.2, max_radius*1.2], showgrid=False, zeroline=False, tickfont=dict(color="#93c5fd"), title=f"Y ({h_unit})", scaleanchor="x", scaleratio=1),
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", font=dict(color="white", size=9), bgcolor="rgba(4, 8, 22, 0.9)")
    )
    st.plotly_chart(fig2d, use_container_width=True, key="grafica_diana_2d", config={"displayModeBar": False})

# --- MÉTRICAS Y RESULTADOS (ESTILO MONOCROMÁTICO NEÓN) ---
st.markdown(f"""
    <div class="metric-card-container">
        <div style="text-align: center; flex: 1;">
            <span style="color: #93c5fd; font-size: 11px; font-weight: bold; text-transform: uppercase;">{txt['diff_height']}</span><br>
            <span style="color: #ffffff; font-size: 17px; font-weight: bold;">{diff_height_display:.2f} {h_unit}</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 240, 255, 0.2); padding-left: 10px; flex: 1;">
            <span style="color: #93c5fd; font-size: 11px; font-weight: bold; text-transform: uppercase;">{txt['sight_angle']}</span><br>
            <span style="color: #ffffff; font-size: 17px; font-weight: bold;">{angulo_deg:.4f}°</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 240, 255, 0.2); padding-left: 10px; flex: 1.2;">
            <span style="color: #93c5fd; font-size: 11px; font-weight: bold; text-transform: uppercase;">{txt['angular_adj']}</span><br>
            <span style="color: #00f0ff; font-size: 17px; font-weight: bold; text-shadow: 0 0 6px rgba(0,240,255,0.5);">{arcmin:.2f} arcmin | {mrad:.2f} mrad</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 240, 255, 0.2); padding-left: 10px; flex: 1.2;">
            <span style="color: #93c5fd; font-size: 11px; font-weight: bold; text-transform: uppercase;">{txt['spot_size_lbl']}</span><br>
            <span style="color: #ffffff; font-size: 17px; font-weight: bold;">Ø {spot_size_display:.2f} {h_unit}</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 240, 255, 0.2); padding-left: 10px; flex: 1.2;">
            <span style="color: #93c5fd; font-size: 11px; font-weight: bold; text-transform: uppercase;">{txt['uncertainty_lbl']}</span><br>
            <span style="color: #38ef7d; font-size: 15px; font-weight: bold; text-shadow: 0 0 6px rgba(56,239,125,0.4);">{uncertainty_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- TABLA DE HISTORIAL BASE DE DATOS SQLITE & EXPORTACIÓN CSV ---
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
            st.markdown('<div class="btn-confirm-yes">', unsafe_allow_html=True)
            if st.button(txt["confirm_yes"], use_container_width=True):
                clear_db()
                st.session_state["confirm_clear"] = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col_no:
            st.markdown('<div class="btn-confirm-cancel">', unsafe_allow_html=True)
            if st.button(txt["confirm_cancel"], use_container_width=True):
                st.session_state["confirm_clear"] = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

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
