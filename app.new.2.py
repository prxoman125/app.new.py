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
    page_title="Simulador de Colimación Óptica",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================================
# 🔒 MÓDULO DE SEGURIDAD CON MARCO HUD ANIMADO DE CARGA Y ESCANEO (AZUL/MORADO NEÓN BRILLANTE)
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
                background-color: #03050c !important;
                overflow-x: hidden;
            }

            /* Fondo Avanzado con Malla Sci-Fi más notoria sin saturar */
            .grid-bg {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: 
                    linear-gradient(rgba(0, 240, 255, 0.08) 1.2px, transparent 1.2px),
                    linear-gradient(90deg, rgba(147, 51, 234, 0.08) 1.2px, transparent 1.2px);
                background-size: 35px 35px, 35px 35px;
                animation: gridMove 25s linear infinite;
                z-index: 0;
                pointer-events: none;
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

            /* Módulos Flotantes Periféricos (Laterales Izquierda y Derecha) */
            .hud-panel-left, .hud-panel-right {
                position: fixed;
                top: 18vh;
                width: 220px;
                padding: 16px;
                background: rgba(5, 12, 25, 0.55);
                border: 1px solid rgba(0, 240, 255, 0.4);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                font-family: monospace;
                font-size: 10px;
                color: #d8b4fe;
                z-index: 1;
                pointer-events: none;
                box-shadow: 0 0 20px rgba(147, 51, 234, 0.15);
                animation: sidePanelEntrance 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }

            .hud-panel-left { left: 4vw; }
            .hud-panel-right { right: 4vw; }

            .panel-header {
                color: #00f0ff;
                font-weight: bold;
                border-bottom: 1px dashed rgba(0, 240, 255, 0.6);
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

            /* Contenedor Exterior con Borde Neon Azul/Morado Muy Brillante */
            .login-wrapper {
                position: relative;
                max-width: 460px;
                margin: 4vh auto 0 auto;
                padding: 2.5px;
                border-radius: 20px;
                background: linear-gradient(135deg, #00f0ff, #c084fc, #00f0ff, #9333ea);
                background-size: 300% 300%;
                animation: borderGlow 5s ease infinite, entranceZoom 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                box-shadow: 0 0 35px rgba(0, 240, 255, 0.45), 0 0 50px rgba(147, 51, 234, 0.35);
            }

            /* Aureola Fina Giratoria Exterior alrededor de la Interfaz Principal (Más Brillante) */
            .aureola-halo {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 540px;
                height: 540px;
                transform: translate(-50%, -50%);
                border: 1.5px dashed rgba(0, 240, 255, 0.85);
                border-radius: 50%;
                animation: haloRotate 20s linear infinite;
                pointer-events: none;
                z-index: 0;
                box-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
            }

            /* Nueva Aureola Fina Giratoria Interior (Más Brillante) */
            .aureola-halo-inner {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 475px;
                height: 475px;
                transform: translate(-50%, -50%);
                border: 1.5px dashed rgba(192, 132, 252, 0.9);
                border-radius: 50%;
                animation: haloRotateReverse 15s linear infinite;
                pointer-events: none;
                z-index: 0;
                box-shadow: 0 0 15px rgba(147, 51, 234, 0.5);
            }

            /* Tarjeta Interior de Login con Glassmorphism Dark Blue/Purple */
            .login-card {
                position: relative;
                background: rgba(6, 10, 22, 0.94);
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
                border-bottom: 1px solid rgba(0, 240, 255, 0.35);
                padding-bottom: 6px;
                text-shadow: 0 0 6px rgba(0, 240, 255, 0.5);
            }

            .loading-bar-container {
                width: 100%;
                height: 3.5px;
                background: rgba(0, 240, 255, 0.15);
                border-radius: 2px;
                overflow: hidden;
                margin-bottom: 15px;
            }

            .loading-bar-fill {
                width: 40%;
                height: 100%;
                background: linear-gradient(90deg, transparent, #00f0ff, #c084fc, transparent);
                box-shadow: 0 0 10px #00f0ff;
                animation: loadingSweep 1.8s ease-in-out infinite;
            }

            /* Contenedor HUD Animado Central */
            .hud-box {
                position: relative;
                width: 130px;
                height: 130px;
                margin: 0 auto 12px auto;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }

            /* Esquinas HUD */
            .corner {
                position: absolute;
                width: 20px;
                height: 20px;
                border-color: #00f0ff;
                border-style: solid;
                animation: cornerPulse 2s infinite alternate ease-in-out;
                z-index: 2;
            }
            .top-left { top: 2px; left: 2px; border-width: 3px 0 0 3px; border-top-left-radius: 4px; }
            .top-right { top: 2px; right: 2px; border-width: 3px 3px 0 0; border-top-right-radius: 4px; }
            .bottom-left { bottom: 2px; left: 2px; border-width: 0 0 3px 3px; border-bottom-left-radius: 4px; }
            .bottom-right { bottom: 2px; right: 2px; border-width: 0 3px 3px 0; border-bottom-right-radius: 4px; }

            /* Anillos Giratorios Internos */
            .hud-ring-outer {
                position: absolute;
                width: 95px;
                height: 95px;
                border: 1.5px dashed rgba(0, 240, 255, 0.75);
                border-radius: 50%;
                animation: rotateRight 9s linear infinite;
                box-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
            }

            .hud-ring-inner {
                position: absolute;
                width: 60px;
                height: 60px;
                border: 1.5px dotted rgba(192, 132, 252, 0.9);
                border-radius: 50%;
                animation: rotateLeft 5s linear infinite;
                box-shadow: 0 0 8px rgba(147, 51, 234, 0.4);
            }

            /* Retícula Crosshair */
            .hud-cross-h { position: absolute; width: 85px; height: 1px; background: rgba(0, 240, 255, 0.6); box-shadow: 0 0 6px #00f0ff; }
            .hud-cross-v { position: absolute; width: 1px; height: 85px; background: rgba(0, 240, 255, 0.6); box-shadow: 0 0 6px #00f0ff; }

            /* Punto Láser Central Azul/Morado Súper Brillante */
            .hud-dot {
                position: absolute;
                width: 8px;
                height: 8px;
                background-color: #00f0ff;
                border-radius: 50%;
                box-shadow: 0 0 14px #00f0ff, 0 0 25px #c084fc, 0 0 35px #9333ea;
                animation: laserPulse 1s infinite ease-in-out;
                z-index: 3;
            }

            /* Scanline Vertical */
            .hud-scanline {
                position: absolute;
                top: -100%;
                left: 0;
                width: 100%;
                height: 35%;
                background: linear-gradient(180deg, rgba(0, 240, 255, 0) 0%, rgba(0, 240, 255, 0.5) 100%);
                border-bottom: 2px solid #00f0ff;
                box-shadow: 0 0 10px #00f0ff;
                animation: scanMove 2.5s infinite ease-in-out;
                z-index: 1;
            }

            /* Títulos del Formulario */
            .login-title {
                color: #ffffff;
                font-size: 18px;
                font-weight: 700;
                text-align: center;
                letter-spacing: 1px;
                text-transform: uppercase;
                margin: 0;
                text-shadow: 0 0 12px rgba(0, 240, 255, 0.7);
            }
            .login-subtitle {
                color: #00f0ff;
                font-size: 10px;
                text-align: center;
                letter-spacing: 0.5px;
                opacity: 0.95;
                margin-top: 4px;
                margin-bottom: 12px;
                font-family: monospace;
                text-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
            }

            /* Resplandor Láser Azul Intenso en Inputs */
            div[data-baseweb="input"] input:focus {
                border-color: #00f0ff !important;
                box-shadow: 0 0 18px rgba(0, 240, 255, 0.8) !important;
            }

            /* Keyframes de Animaciones */
            @keyframes haloRotate {
                from { transform: translate(-50%, -50%) rotate(0deg); }
                to { transform: translate(-50%, -50%) rotate(360deg); }
            }

            @keyframes haloRotateReverse {
                from { transform: translate(-50%, -50%) rotate(360deg); }
                to { transform: translate(-50%, -50%) rotate(0deg); }
            }

            @keyframes entranceZoom {
                0% { opacity: 0; transform: scale(0.92) translateY(-20px); }
                100% { opacity: 1; transform: scale(1) translateY(0); }
            }

            @keyframes sidePanelEntrance {
                0% { opacity: 0; transform: translateY(30px); }
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

            @keyframes gridMove {
                0% { background-position: 0 0, 0 0; }
                100% { background-position: 35px 35px, 35px 35px; }
            }

            @keyframes rotateRight {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            @keyframes rotateLeft {
                from { transform: rotate(0deg); }
                to { transform: rotate(-360deg); }
            }

            @keyframes cornerPulse {
                0% { border-color: #00f0ff; filter: drop-shadow(0 0 5px #00f0ff); }
                100% { border-color: #c084fc; filter: drop-shadow(0 0 12px #c084fc); }
            }

            @keyframes laserPulse {
                0%, 100% { transform: scale(0.85); opacity: 0.8; }
                50% { transform: scale(1.4); opacity: 1; }
            }

            @keyframes scanMove {
                0% { top: -40%; }
                50% { top: 100%; }
                100% { top: -40%; }
            }

            /* Ocultar elementos decorativos en dispositivos móviles */
            @media (max-width: 1024px) {
                .hud-panel-left, .hud-panel-right, .aureola-halo, .aureola-halo-inner { display: none; }
            }
        </style>

        <div class="grid-bg"></div>

        <div class="top-global-hud">
            <span>● SYSTEM: ONLINE</span>
            <span>ENCRYPTION: AES-256</span>
            <span>NODE: OPTIC-CORE-01</span>
        </div>

        <div class="hud-panel-left">
            <div class="panel-header">DIAGNOSTICO_RED</div>
            <div class="hud-data-row"><span>LATENCIA:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">12 ms</span></div>
            <div class="hud-data-row"><span>SENSORES:</span><span style="color:#38ef7d; text-shadow:0 0 6px #38ef7d">CALIBRADOS</span></div>
            <div class="hud-data-row"><span>OPTICAL LASER:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">READY</span></div>
            <div class="hud-data-row"><span>SEGURIDAD:</span><span style="color:#38ef7d; text-shadow:0 0 6px #38ef7d">ACTIVA</span></div>
        </div>

        <div class="hud-panel-right">
            <div class="panel-header">MODULO_TELEMETRIA</div>
            <div class="hud-data-row"><span>CPU CORE:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">1.4 GHz</span></div>
            <div class="hud-data-row"><span>MEMORIA:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">18% REQ</span></div>
            <div class="hud-data-row"><span>CANAL:</span><span style="color:#00f0ff; text-shadow:0 0 6px #00f0ff">0xFA992</span></div>
            <div class="hud-data-row"><span>SSL LINK:</span><span style="color:#38ef7d; text-shadow:0 0 6px #38ef7d">ESTABLE</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 1.3, 1])
    
    with col_center:
        st.markdown("""
            <div class="login-wrapper">
                <div class="aureola-halo"></div>
                <div class="aureola-halo-inner"></div>
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
                        <div class="hud-ring-inner"></div>
                        <div class="hud-dot"></div>
                        <div class="hud-scanline"></div>
                    </div>
                    <div class="login-title">Autenticación Óptica</div>
                    <div class="login-subtitle">● SISTEMA DE AVALÚO Y COLIMACIÓN LÁSER</div>
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
                    
                    with st.spinner("🔍 Escaneando parámetros y calibrando sensores..."):
                        time.sleep(1.2)
                    st.rerun()
                else:
                    st.session_state.intentos += 1
                    intentos_restantes = MAX_INTENTOS - st.session_state.intentos
                    st.error(f"Credenciales incorrectas. Intentos restantes: {intentos_restantes}")
                    st.stop()

if not st.session_state.autenticado:
    st.stop()


# =========================================================================
# 👇 CÓDIGO DEL SIMULADOR A CONTINUACIÓN (UNIFICADO CON ESTÉTICA AZUL/MORADO NEÓN)
# =========================================================================

# --- BASE DE DATOS SQLITE ---
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
        (perfil, distancia, h_mira, h_extra, spot_size, angulo, moa, mrad, direccion, clics_moa, pulsos_mrad, incertidumbre)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        rec["Perfil / Carrera"], rec["Distancia"], rec["Línea Colimación"], 
        rec["Desviación Impacto"], rec["Spot Size"], rec["Ángulo (α)"], 
        rec["MOA"], rec["mrad"], rec["Dirección"], rec["Clics (1/4 MOA)"], 
        rec["Pulsos (0.1 mrad)"], rec["Incertidumbre (±)"]
    ))
    conn.commit()
    conn.close()

def load_history_from_db():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id, fecha AS 'Fecha/Hora', perfil AS 'Perfil / Carrera', distancia AS 'Distancia', h_mira AS 'Línea Colimación', h_extra AS 'Desviación Impacto', spot_size AS 'Spot Size', angulo AS 'Ángulo (α)', moa AS 'MOA', mrad AS 'mrad', direccion AS 'Dirección', clics_moa AS 'Clics (1/4 MOA)', pulsos_mrad AS 'Pulsos (0.1 mrad)', incertidumbre AS 'Incertidumbre (±)' FROM historial ORDER BY id DESC", conn)
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

# --- ESTILOS CSS PERSONALIZADOS (AZUL/MORADO NEÓN GLOW & SLIM LAYOUT) ---
st.markdown("""
    <style>
        /* Ocultar Barra Superior y Toolbar de Streamlit */
        header, [data-testid="stHeader"], [data-testid="stToolbar"] {
            visibility: hidden !important;
            height: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
        }

        /* Ajuste de márgenes globales del contenedor */
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
            animation: fadeIn 0.8s ease-out;
        }

        .stApp {
            background-color: #03050c !important;
            color: #f3e8ff !important;
        }

        /* Estilo de la Barra Lateral */
        [data-testid="stSidebar"] {
            background-color: #070b19 !important;
            border-right: 1px solid rgba(0, 149, 255, 0.25) !important;
            box-shadow: 4px 0px 18px rgba(147, 51, 234, 0.08);
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
            border-bottom: 1px solid rgba(0, 149, 255, 0.2) !important;
            padding-bottom: 4px;
            text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
        }

        /* Botones Interactivos */
        div.stButton > button {
            background: linear-gradient(135deg, #0b132b 0%, #171033 100%) !important;
            color: #00f0ff !important;
            border: 1px solid rgba(0, 149, 255, 0.4) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 0 10px rgba(0, 149, 255, 0.1);
        }
        div.stButton > button:hover {
            background: #00f0ff !important;
            color: #03050c !important;
            box-shadow: 0px 0px 18px rgba(0, 240, 255, 0.6) !important;
            border-color: #00f0ff !important;
            transform: translateY(-1px);
        }

        /* Microinteracciones para Steppers (- / +) */
        button[aria-label="Increase value"], 
        button[aria-label="Decrease value"],
        div[data-baseweb="spinbutton"] button,
        [data-testid="stNumberInputStepDown"],
        [data-testid="stNumberInputStepUp"] {
            color: #00f0ff !important;
            background-color: #0b132b !important;
            border-color: rgba(0, 149, 255, 0.3) !important;
            transition: all 0.25s ease !important;
        }

        button[aria-label="Increase value"]:hover, 
        button[aria-label="Decrease value"]:hover,
        div[data-baseweb="spinbutton"] button:hover,
        [data-testid="stNumberInputStepDown"]:hover,
        [data-testid="stNumberInputStepUp"]:hover {
            background-color: #00f0ff !important;
            color: #03050c !important;
            box-shadow: 0px 0px 12px rgba(0, 240, 255, 0.5) !important;
            border-color: #00f0ff !important;
        }

        /* Campos de Entrada e Selects */
        div[data-baseweb="input"], div[data-baseweb="select"] > div {
            background-color: #0b132b !important;
            border: 1px solid rgba(0, 149, 255, 0.25) !important;
            color: #ffffff !important;
            border-radius: 6px !important;
            transition: all 0.3s ease !important;
        }

        div[data-baseweb="input"]:hover, div[data-baseweb="select"] > div:hover {
            border-color: rgba(0, 149, 255, 0.6) !important;
            box-shadow: 0 0 10px rgba(0, 149, 255, 0.25) !important;
        }

        /* Tarjetas de Métricas con Glow Dinámico Azul/Morado Neón */
        .metric-card-container {
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: linear-gradient(135deg, #070b19 0%, #100f2b 100%);
            border: 1px solid rgba(0, 149, 255, 0.35); 
            padding: 16px 20px; 
            border-radius: 12px; 
            margin-top: 15px; 
            margin-bottom: 25px;
            box-shadow: 0 0 20px rgba(147, 51, 234, 0.15);
            animation: pulseGlow 4s infinite alternate ease-in-out, slideUp 0.6s ease-out;
        }

        /* Confirmaciones */
        div.btn-confirm-yes > div.stButton > button {
            background: linear-gradient(135deg, #092c1d 0%, #114e34 100%) !important;
            color: #38ef7d !important;
            border: 1px solid #114e34 !important;
        }
        div.btn-confirm-yes > div.stButton > button:hover {
            background: #38ef7d !important;
            color: #000000 !important;
            box-shadow: 0px 0px 15px rgba(56, 239, 125, 0.5);
        }

        div.btn-confirm-cancel > div.stButton > button {
            background: linear-gradient(135deg, #380e14 0%, #5d1621 100%) !important;
            color: #ff4d4d !important;
            border: 1px solid #5d1621 !important;
        }
        div.btn-confirm-cancel > div.stButton > button:hover {
            background: #ff4d4d !important;
            color: #000000 !important;
            box-shadow: 0px 0px 15px rgba(255, 77, 77, 0.5);
        }

        /* Keyframes de Animaciones Generales */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulseGlow {
            0% { box-shadow: 0 0 15px rgba(0, 149, 255, 0.12), inset 0 0 10px rgba(147, 51, 234, 0.05); }
            100% { box-shadow: 0 0 25px rgba(0, 149, 255, 0.3), inset 0 0 15px rgba(147, 51, 234, 0.1); }
        }
    </style>
""", unsafe_allow_html=True)

# --- DICCIONARIOS DE TRADUCCIÓN ---
TEXTS = {
    "ES": {
        "title": "Simulador de Alineación y Colimación Óptica Avanzado",
        "lang_select": "Idioma / Language",
        "unit_select": "Sistema de Unidades / Unit System",
        "metric": "Métrico (cm, metros)",
        "imperial": "Imperial (pulgadas, yardas)",
        "profile_select": "Perfil de Aplicación / Profesión",
        "profile_placeholder": "-- Seleccione una Profesión / Carrera --",
        "p1": "Calibración de brazos robóticos (Rango muy corto)",
        "p2": "Alineación de maquinaria industrial (Rango corto)",
        "p3": "Topografía y construcción civil (Rango medio)",
        "p4": "Alineación de colectores solares / Helióstatos (Rango medio-largo)",
        "p5": "Guiado láser de robótica móvil (Rango largo)",
        "p6": "Guiado de maquinaria de tunelación (Rango largo-extremo)",
        "p7": "Alineación de Puentes Colgantes (Rango Largo)",
        "p8": "Nivelación de Vías de Tren de Alta Velocidad (Rango Medio)",
        "p9": "Montacargas Autónomos en Almacenes 3D (Rango Corto)",
        "p10": "Clasificación de Paquetes por Bandas (Rango Muy Corto)",
        "p11": "Alineación de Antenas Satelitales (Rango Extremo)",
        "p12": "Calibración de Sensores de Aterrizaje (Rango Medio)",
        "p13": "Alineación de Hélices en Torres Eólicas (Rango Corto)",
        "p14": "Inspección Óptica de Cascos de Barcos (Rango Medio)",
        "p15": "Guiado de Perforadoras en Minería (Rango Largo)",
        "p16": "Colimación de Telescopios Astronómicos (Rango Extremo)",
        "p17": "Alineación de Espejos Láser Quirúrgicos (Rango Muy Corto)",
        "p18": "Guiado Optoelectrónico de Misiles Defensivos (Rango Extremo)",
        "p19": "Calibración de Sensores LiDAR Automotrices (Rango Medio)",
        "p20": "Centrado de Turbinas Hidroeléctricas (Rango Corto)",
        "p21": "Inspección de Deformación en Turbinas de Gas (Rango Corto)",
        "p22": "Nivelación de Plataformas Petroleras Offshore (Rango Medio-Largo)",
        "p23": "Alineación de Escáneres LiDAR en Drones (Rango Medio)",
        "p24": "Colimación de Sistemas Ópticos Micro litográficos (Rango Muy Corto)",
        "p25": "Control de Flexión en Estructuras de Estadios (Rango Medio)",

        "params": "Parámetros Geométricos",
        "phys_params": "Óptica & Entorno Físico",
        "reset_btn": "Reiniciar Valores a 0",
        "save_btn": "💾 Registrar Medición (DB)",
        "export_csv": "📥 Exportar Historial (CSV)",
        "h_mira": "Línea de colimación",
        "h_extra": "Desviación del punto de impacto / Objetivo",
        "dist_input": "Distancia al receptor / Destino",
        "ref_angle_input": "Inclinación eje referencia (°)",
        "laser_div": "Divergencia Láser (mrad)",
        "temp_input": "Temperatura (°C)",
        "press_input": "Presión Atm. (hPa)",
        "earth_curv": "Activar Curvatura Terrestre",
        "cm": "cm",
        "m": "m",
        "in": "pulgadas",
        "yd": "yardas",
        "laser_label": "Eje óptico de referencia",
        "sight_label": "Eje del sensor ajustable",
        "target_center": "Centro del Objetivo",
        "target_point": "Punto Requerido",
        "title_graph": "Distancia",
        "req_angle": "Ángulo Requerido (α)",
        "diff_height": "Diferencia Altura Total",
        "sight_angle": "Ángulo de Inclinación (α)",
        "angular_adj": "Ajuste Angular",
        "direction": "Dirección",
        "direction_up": "Arriba",
        "direction_down": "Abajo",
        "spot_size_lbl": "Diámetro de Haz (Spot)",
        "curv_drop_lbl": "Caída x Curvatura",
        "uncertainty_lbl": "Incertidumbre (SciPy)",
        "history_title": "Historial en Base de Datos (SQLite)",
        "clear_history": "Borrar Base de Datos",
        "confirm_clear_msg": "¿Estás seguro de que deseas borrar toda la base de datos?",
        "confirm_yes": "✔ Sí, Borrar",
        "confirm_cancel": "✖ Cancelar",
        "empty_history": "No hay registros guardados en la base de datos.",
        "select_prompt": "⚠️ Por favor, seleccione un Perfil de Aplicación / Profesión en la barra lateral para iniciar la simulación.",
        "record_saved": "✅ Medición guardada permanentemente en SQLite.",
        "target_2d_title": "🎯 Vista Frontal 2D (Retícula / Diana)"
    },
    "EN": {
        "title": "Advanced Optical Alignment & Collimation Simulator",
        "lang_select": "Language / Idioma",
        "unit_select": "Unit System / Sistema de Unidades",
        "metric": "Metric (cm, meters)",
        "imperial": "Imperial (inches, yards)",
        "profile_select": "Application Profile / Profession",
        "profile_placeholder": "-- Select a Profession / Career --",
        "p1": "Robotic Arm Calibration (Very Short Range)",
        "p2": "Industrial Machinery Alignment (Short Range)",
        "p3": "Surveying & Civil Construction (Medium Range)",
        "p4": "Solar Collector / Heliostat Alignment (Medium-Long Range)",
        "p5": "Mobile Robotics Laser Guidance (Long Range)",
        "p6": "Tunneling Machinery Guidance (Long-Extreme Range)",
        "p7": "Suspension Bridge Alignment (Long Range)",
        "p8": "High-Speed Train Track Leveling (Medium Range)",
        "p9": "Autonomous Forklifts in 3D Warehouses (Short Range)",
        "p10": "Belt Package Sorting Systems (Very Short Range)",
        "p11": "Satellite Dish Alignment (Extreme Range)",
        "p12": "Aircraft Landing Sensor Calibration (Medium Range)",
        "p13": "Wind Turbine Blade Alignment (Short Range)",
        "p14": "Ship Hull Optical Inspection (Medium Range)",
        "p15": "Open-Pit Mining Drill Guidance (Long Range)",
        "p16": "Astronomical Telescope Collimation (Extreme Range)",
        "p17": "Surgical Laser Mirror Alignment (Very Short Range)",
        "p18": "Defensive Missile Optoelectronic Guidance (Extreme Range)",
        "p19": "Automotive LiDAR Sensor Calibration (Medium Range)",
        "p20": "Hydroelectric Turbine Centering (Short Range)",
        "p21": "Gas Turbine Strain Inspection (Short Range)",
        "p22": "Offshore Oil Rig Platform Leveling (Medium-Long Range)",
        "p23": "Drone LiDAR Scanner Alignment (Medium Range)",
        "p24": "Microlithographic Optical System Collimation (Very Short Range)",
        "p25": "Stadium Roof Deflection Monitoring (Medium Range)",

        "params": "Geometric Parameters",
        "phys_params": "Optics & Physical Environment",
        "reset_btn": "Reset Values to 0",
        "save_btn": "💾 Save Measurement (DB)",
        "export_csv": "📥 Export History (CSV)",
        "h_mira": "Collimation Line",
        "h_extra": "Impact Point Deviation / Target Offset",
        "dist_input": "Distance to Receiver / Destination",
        "ref_angle_input": "Ref. Axis Inclination (°)",
        "laser_div": "Laser Divergence (mrad)",
        "temp_input": "Temperature (°C)",
        "press_input": "Atm. Pressure (hPa)",
        "earth_curv": "Enable Earth Curvature",
        "cm": "cm",
        "m": "m",
        "in": "inches",
        "yd": "yards",
        "laser_label": "Reference Optical Axis",
        "sight_label": "Adjustable Sensor Axis",
        "target_center": "Target Center",
        "target_point": "Required Point",
        "title_graph": "Distance",
        "req_angle": "Required Angle (α)",
        "diff_height": "Total Height Diff.",
        "sight_angle": "Inclination Angle (α)",
        "angular_adj": "Angular Adjustment",
        "direction": "Direction",
        "direction_up": "Up",
        "direction_down": "Down",
        "spot_size_lbl": "Beam Diameter (Spot)",
        "curv_drop_lbl": "Curvature Drop",
        "uncertainty_lbl": "Uncertainty (SciPy)",
        "history_title": "Database Records (SQLite)",
        "clear_history": "Clear Database",
        "confirm_clear_msg": "Are you sure you want to clear the entire database?",
        "confirm_yes": "✔ Yes, Clear",
        "confirm_cancel": "✖ Cancel",
        "empty_history": "No records saved in database yet.",
        "select_prompt": "⚠️ Please select an Application Profile / Profession in the sidebar to start the simulation.",
        "record_saved": "✅ Measurement saved permanently into SQLite.",
        "target_2d_title": "🎯 Vista Frontal 2D (Retícula / Diana)"
    }
}

# --- SELECCIÓN DE IDIOMA ---
st.sidebar.header("Configuración / Settings")
lang = st.sidebar.selectbox("Idioma / Language", ["Español", "English"])
lang_code = "ES" if lang == "Español" else "EN"
txt = TEXTS[lang_code]

# --- MENÚ DESPLEGABLE DE PROFESIONES ---
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

# --- ENCABEZADO PRINCIPAL (CON LUZ NEÓN AZUL/MORADO) ---
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #070b19 0%, #110e28 100%);
                padding: 14px 25px;
                border-radius: 12px;
                border-left: 5px solid #00f0ff;
                border: 1px solid rgba(0, 149, 255, 0.3);
                margin-bottom: 20px;
                box-shadow: 0px 4px 20px rgba(147, 51, 234, 0.15);">
        <h2 style="color: #ffffff; margin: 0; font-size: 24px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; letter-spacing: 1px; text-shadow: 0 0 10px rgba(0,240,255,0.3);">
            {txt['title']}
        </h2>
        <p style="color: #c084fc; margin: 0; font-size: 13px; opacity: 0.9;">
            Alineación de precisión óptica & Física Atmosférica | Perfil Activo: <b style="color: #00f0ff;">{profile if profile != txt['profile_placeholder'] else 'Ninguno'}</b>
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

# --- REGISTRO A BASE DE DATOS EN SQLite ---
if save_clicked:
    current_record = {
        "Perfil / Carrera": profile,
        "Distancia": f"{D_val:.1f} {d_unit}",
        "Línea Colimación": f"{H_mira:.2f} {h_unit}",
        "Desviación Impacto": f"{H_extra:.2f} {h_unit}",
        "Spot Size": f"{spot_size_display:.2f} {h_unit}",
        "Ángulo (α)": f"{angulo_deg:.4f}°",
        "MOA": moa,
        "mrad": mrad,
        "Dirección": direccion_str,
        "Clics (1/4 MOA)": clicks_moa,
        "Pulsos (0.1 mrad)": pulsos_mrad,
        "Incertidumbre (±)": uncertainty_str
    }
    save_record_to_db(current_record)
    st.sidebar.success(txt["record_saved"])

# --- GRÁFICAS 3D Y 2D CON CONTENEDORES AZUL/MORADO NEÓN ---
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
        colorscale=[[0, '#03050c'], [1, '#0e1124']],
        showscale=False, opacity=0.6, hoverinfo='none'
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[0, D_cm], y=[0, 0], z=[0, y_ref_end],
        mode='lines+markers',
        name=f"{txt['laser_label']} ({ref_angle_deg:.2f}°)",
        line=dict(color='#00d9ff', width=7, dash='dash'),
        marker=dict(size=4, color='#00d9ff')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[0, D_cm], y=[0, 0], z=[pos_mira[1], pos_impacto_mira[1]],
        mode='lines+markers',
        name=f"{txt['sight_label']} (α = {angulo_deg:.2f}°)",
        line=dict(color='#00f0ff', width=9),
        marker=dict(size=5, color='#00f0ff')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[D_cm], y=[0], z=[y_ref_end],
        mode='markers', name=txt["target_center"],
        marker=dict(size=8, color='#ffe600', symbol='circle')
    ))

    fig3d.add_trace(go.Scatter3d(
        x=[D_cm], y=[0], z=[y_target_point],
        mode='markers', name=txt["target_point"],
        marker=dict(size=10, color='#00ff66', symbol='diamond')
    ))

    fig3d.update_layout(
        title=dict(
            text=f"📐 <b>{txt['title_graph']} 3D</b>: {D_val:.1f} {d_unit} | <b>α</b>: {angulo_deg:.4f}°",
            font=dict(color="#00f0ff", size=14)
        ),
        paper_bgcolor='#050814', plot_bgcolor='#050814',
        height=460, margin=dict(l=5, r=5, t=35, b=5),
        scene=dict(
            aspectmode='manual', aspectratio=dict(x=2.0, y=1, z=1.1),
            xaxis=dict(title='Distancia (cm)', backgroundcolor="#050814", gridcolor="#132347", tickfont=dict(color="#c084fc")),
            yaxis=dict(title='Eje Lateral', backgroundcolor="#050814", gridcolor="#132347", tickfont=dict(color="#c084fc")),
            zaxis=dict(title='Elevación (cm)', backgroundcolor="#050814", gridcolor="#132347", tickfont=dict(color="#c084fc")),
            camera=dict(eye=dict(x=1.6, y=-1.4, z=0.6))
        ),
        legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", font=dict(color="white", size=10), bgcolor="rgba(11, 19, 43, 0.85)")
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
            line=dict(color="#291b4a", width=1.5),
            fillcolor="rgba(30, 20, 60, 0.2)"
        )

    fig2d.add_shape(type="line", x0=-max_radius*1.2, y0=0, x1=max_radius*1.2, y1=0, line=dict(color="#3b246b", width=1, dash="dot"))
    fig2d.add_shape(type="line", x0=0, y0=-max_radius*1.2, x1=0, y1=max_radius*1.2, line=dict(color="#3b246b", width=1, dash="dot"))

    fig2d.add_shape(
        type="circle", xref="x", yref="y",
        x0=-spot_radius_cm, y0=diferencia_altura_cm - spot_radius_cm,
        x1=spot_radius_cm, y1=diferencia_altura_cm + spot_radius_cm,
        line=dict(color="#00f0ff", width=2),
        fillcolor="rgba(0, 240, 255, 0.35)"
    )

    fig2d.add_trace(go.Scatter(
        x=[0], y=[diferencia_altura_cm],
        mode='markers', name=txt["target_point"],
        marker=dict(size=8, color='#00ff66', symbol='cross')
    ))

    fig2d.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers', name=txt["target_center"],
        marker=dict(size=7, color='#ffe600', symbol='circle')
    ))

    fig2d.update_layout(
        title=dict(text=txt["target_2d_title"], font=dict(color="#00f0ff", size=14)),
        paper_bgcolor='#050814', plot_bgcolor='#050814',
        height=460, margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(range=[-max_radius*1.2, max_radius*1.2], showgrid=False, zeroline=False, tickfont=dict(color="#c084fc"), title=f"X ({h_unit})"),
        yaxis=dict(range=[-max_radius*1.2, max_radius*1.2], showgrid=False, zeroline=False, tickfont=dict(color="#c084fc"), title=f"Y ({h_unit})", scaleanchor="x", scaleratio=1),
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", font=dict(color="white", size=9), bgcolor="rgba(11, 19, 43, 0.85)")
    )
    st.plotly_chart(fig2d, use_container_width=True, key="grafica_diana_2d")

# --- MÉTRICAS Y RESULTADOS (ESTILO AZUL/MORADO NEÓN PULSANTE) ---
st.markdown(f"""
    <div class="metric-card-container">
        <div style="text-align: center; flex: 1;">
            <span style="color: #c084fc; font-size: 11px; font-weight: bold; text-transform: uppercase;">{txt['diff_height']}</span><br>
            <span style="color: #ffffff; font-size: 17px; font-weight: bold;">{diff_height_display:.2f} {h_unit}</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 149, 255, 0.25); padding-left: 10px; flex: 1;">
            <span style="color: #c084fc; font-size: 11px; font-weight: bold; text-transform: uppercase;">{txt['sight_angle']}</span><br>
            <span style="color: #ffffff; font-size: 17px; font-weight: bold;">{angulo_deg:.4f}°</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 149, 255, 0.25); padding-left: 10px; flex: 1.2;">
            <span style="color: #c084fc; font-size: 11px; font-weight: bold; text-transform: uppercase;">{txt['angular_adj']}</span><br>
            <span style="color: #00f0ff; font-size: 17px; font-weight: bold; text-shadow: 0 0 8px rgba(0,240,255,0.5);">{moa:.2f} MOA | {mrad:.2f} mrad</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 149, 255, 0.25); padding-left: 10px; flex: 1.2;">
            <span style="color: #c084fc; font-size: 11px; font-weight: bold; text-transform: uppercase;">{txt['spot_size_lbl']}</span><br>
            <span style="color: #ffffff; font-size: 17px; font-weight: bold;">Ø {spot_size_display:.2f} {h_unit}</span>
        </div>
        <div style="text-align: center; border-left: 1px solid rgba(0, 149, 255, 0.25); padding-left: 10px; flex: 1.2;">
            <span style="color: #c084fc; font-size: 11px; font-weight: bold; text-transform: uppercase;">{txt['uncertainty_lbl']}</span><br>
            <span style="color: #38ef7d; font-size: 15px; font-weight: bold; text-shadow: 0 0 8px rgba(56,239,125,0.4);">{uncertainty_str}</span>
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
            file_name="historial_colimacion.csv",
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
            if st.button(txt["confirm_confirm_cancel"] if "confirm_confirm_cancel" in txt else txt["confirm_cancel"], use_container_width=True):
                st.session_state["confirm_clear"] = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

if not df_db.empty:
    st.dataframe(
        df_db,
        use_container_width=True,
        hide_index=True,
        column_config={
            "MOA": st.column_config.NumberColumn("MOA", format="%.2f"),
            "mrad": st.column_config.NumberColumn("mrad", format="%.2f"),
        }
