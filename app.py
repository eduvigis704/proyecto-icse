import streamlit as st
from docx import Document
import json
import os
from io import BytesIO
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Proyecto Intermodular ICSE", page_icon="🔬", layout="centered")

# --- ESTILOS PERSONALIZADOS (Colores ICSE) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #13263d;
        color: white;
    }
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    /* Estilo para botones normales */
    .stButton>button { 
        background-color: #0569b3 !important; 
        color: white !important; 
        border-radius: 10px !important; 
        border: 2px solid #ffffff !important; 
        height: 3em !important; 
        width: 100% !important; 
        font-weight: bold !important;
    }
    .stButton>button:hover { 
        border: 2px solid #ec6216 !important; 
        color: #ec6216 !important; 
        background-color: white !important; 
    }
    
    /* Estilo ESPECÍFICO para el botón de descarga (Naranja para destacar) */
    [data-testid="stDownloadButton"]>button {
        background-color: #ec6216 !important; 
        color: white !important; 
        border-radius: 10px !important; 
        border: 2px solid #ffffff !important; 
        height: 3.5em !important; 
        width: 100% !important; 
        font-weight: bold !important;
        font-size: 18px !important;
    }
    [data-testid="stDownloadButton"]>button:hover {
        border: 2px solid #0569b3 !important; 
        color: #0569b3 !important; 
        background-color: white !important;
    }

    div.stTextArea textarea { border: 2px solid #0569b3; border-radius: 10px; }
    
    /* Forzar color de texto base a blanco y títulos a naranja */
    .stMarkdown, p, li { color: white !important; }
    h1, h2, h3, h4 { color: #ec6216 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS DE CONTENIDO ---
PROYECTOS = {
    "proyecto1": {
        "nombre": "Laboratorio de Diagnóstico Microbiológico",
        "mision": "Diseñar un laboratorio centrado en el cultivo, aislamiento e identificación de microorganismos patógenos y estudios de sensibilidad a antimicrobianos.",
        "fases": [
            {
                "id": "f1", "nombre": "Fase 1: Identificación de necesidades",
                "preguntas": [
                    {
                        "id": "p1_f1_q1", 
                        "texto": "1. ¿Por qué es necesario este servicio tras el aumento de infecciones nosocomiales y resistencias a antibióticos?",
                        "pistas": ["Pista 1: Busca de qué se encarga un laboratorio centrado en el cultivo.", 
                                   "Pista 2: Piensa en qué implica que haya un aumento de infecciones nosocomiales.", 
                                   "Pista 3: Relaciona la resistencia a los antibióticos con el tiempo de diagnóstico.", 
                                   "Pista 4: Considera el impacto en la saturación hospitalaria del Servicio Canario de Salud.", 
                                   "Pista 5: ¿Cómo ayudaría un diagnóstico microbiológico rápido a reducir el coste y mejorar el tratamiento?"]
                    },
                    {
                        "id": "p1_f1_q2", 
                        "texto": "2. Diseña el organigrama y busca subvenciones aplicables.",
                        "pistas": ["Pista 1: ¿Qué áreas necesita un laboratorio de este tipo? (Recepción, siembra, etc.).", 
                                   "Pista 2: Busca en el BOC (Boletín Oficial de Canarias) o fondos FEDER.", 
                                   "Pista 3: Investiga sobre ayudas a la innovación tecnológica en salud.", 
                                   "Pista 4: No olvides la figura del Facultativo Especialista.", 
                                   "Pista 5: Estructura de arriba (Dirección) hacia abajo (Técnicos de Laboratorio)."]
                    }
                ]
            }
        ]
    },
    "proyecto2": {"nombre": "Laboratorio de Biología Molecular", "mision": "Diseñar un laboratorio de extracción y PCR.", "fases": []},
    "proyecto3": {"nombre": "Laboratorio de Bioquímica y Hematología", "mision": "Diseñar un laboratorio de alta rotación.", "fases": []}
}

# --- FUNCIONES DE PERSISTENCIA ---
def cargar_datos():
    if os.path.exists("db_proyectos.json"):
        with open("db_proyectos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"proyecto1": {}, "proyecto2": {}, "proyecto3": {}}

def guardar_datos(datos):
    with open("db_proyectos.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

def generar_docx(usuario, datos_usuario):
    doc = Document()
    doc.add_heading(f"Proyecto Intermodular - {usuario.upper()}", 0)
    for fase in PROYECTOS[usuario]["fases"]:
        doc.add_heading(fase["nombre"], level=1)
        for preg in fase["preguntas"]:
            doc.add_heading(preg["texto"], level=2)
            res = datos_usuario.get(preg["id"], "Sin respuesta.")
            doc.add_paragraph(res)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- LÓGICA DE INTERFAZ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""

# Cabecera con logo usando la imagen local
col_a, col_b, col_c = st.columns([1, 2, 1])
with col_b:
    try:
        imagen_logo = Image.open("logo-vector-icse-vertical.webp")
        st.image(imagen_logo, use_container_width=True)
    except Exception as e:
        st.warning("⚠️ No se encontró la imagen 'logo-vector-icse-vertical.webp'. Revisa que esté en la misma carpeta.")

st.markdown("---")

if not st.session_state.logged_in:
    st.title("Inicio de Sesión - CDI BioTech")
    user_input = st.text_input("Usuario (proyecto1, proyecto2, proyecto3 o admin_icse):").lower().strip()
    if st.button("ENTRAR"):
        if user_input in ["proyecto1", "proyecto2", "proyecto3", "admin_icse"]:
            st.session_state.logged_in = True
            st.session_state.user = user_input
            st.rerun()
        else:
            st.error("Usuario no válido.")
else:
    # --- PANEL DE PROFESORA (ADMIN) ---
    if st.session_state.user == "admin_icse":
        st.title("👨‍🏫 Panel de Control Docente")
        db = cargar_datos()
        for p_id, p_info in PROYECTOS.items():
            with st.expander(f"Ver progreso: {p_info['nombre']}"):
                respuestas = db.get(p_id, {})
                if not respuestas: st.write("Aún no hay respuestas.")
                for fid, res in respuestas.items():
                    st.info(f"**Pregunta {fid}:** {res}")
        if st.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.rerun()

    # --- PANEL DE ALUMNO ---
    else:
        user = st.session_state.user
        db = cargar_datos()
        
        st.sidebar.title(f"Hola, {user}")
        if st.sidebar.button("Cerrar Sesión (Pausa)"):
            st.warning("Recuerda que para guardar en el .docx final debes pulsar 'Guardar Fase'.")
            st.session_state.logged_in = False
            st.rerun()

        st.title(f"🚀 {PROYECTOS[user]['nombre']}")
        st.markdown(f"**Misión:** {PROYECTOS[user]['mision']}")
        
        tab1, tab2 = st.tabs(["Macro-Reto", "Fases del Proyecto"])
        
        with tab1:
            st.write("El Servicio Canario de la Salud ha emitido una licitación pública de urgencia. Se requiere la creación y puesta en marcha del 'Complejo Diagnóstico Integral (CDI) BioTech Canarias', unas instalaciones de vanguardia diseñadas para descongestionar la red hospitalaria pública y ofrecer servicios de diagnóstico rápido, medicina personalizada y control epidemiológico.")
            st.write("El problema: El complejo es demasiado grande para ser diseñado por un solo equipo. Necesita que se planifiquen, desde cero y de forma paralela, tres laboratorios especializados. Haz click en la pestaña superior 'Fases del Proyecto' para comenzar a trabajar en tu departamento asignado.")
        
        with tab2:
            fases_disponibles = [f["nombre"] for f in PROYECTOS[user]["fases"]]
            if fases_disponibles:
                fase_sel = st.selectbox("Selecciona la Fase:", fases_disponibles)
                fase_data = next(f for f in PROYECTOS[user]["fases"] if f["nombre"] == fase_sel)
                
                for p in fase_data["preguntas"]:
                    st.subheader(p["texto"])
                    # Recuperar respuesta guardada
                    val_previo = db[user].get(p["id"], "")
                    res_alumno = st.text_area("Escribe aquí tu respuesta:", value=val_previo, key=p["id"])
                    
                    # --- NUEVO SISTEMA DE PISTAS MEJORADO ---
                    hint_key = f"hint_state_{p['id']}"
                    if hint_key not in st.session_state: 
                        st.session_state[hint_key] = -1 # -1 significa que no se ha pulsado nada
                    
                    state = st.session_state[hint_key]
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if state == -1:
                            if st.button("💡 Pista (?)", key=f"start_{p['id']}"):
                                st.session_state[hint_key] = 0
                                st.rerun()
                        elif state >= len(p["pistas"]):
                            st.info("Ya no hay más pistas, para volver a ver la guía pulsa el botón 'Pista(?)'")
                            if st.button("💡 Pista (?)", key=f"reset_{p['id']}"):
                                st.session_state[hint_key] = 0
                                st.rerun()
                        else:
                            st.warning(p["pistas"][state])
                            if st.button("Siguiente pista >>", key=f"next_{p['id']}"):
                                st.session_state[hint_key] += 1
                                st.rerun()

                st.markdown("---")
                # Botón de Guardado
                if st.button("💾 GUARDAR RESPUESTAS EN EL SERVIDOR"):
                    for p in fase_data["preguntas"]:
                        db[user][p["id"]] = st.session_state[p["id"]]
                    guardar_datos(db)
                    st.success("¡Progreso guardado correctamente! Ya puedes descargar el documento final actualizado.")
                
                # Botón de Descarga Siempre Visible e Independiente
                st.markdown("#### Entrega del Proyecto")
                st.write("Si ya has guardado tus respuestas, descárgate el documento final para entregarlo a tus profesores:")
                docx_file = generar_docx(user, db[user])
                st.download_button(label="📥 Descargar Documento .docx para entregar", 
                                   data=docx_file, 
                                   file_name=f"Proyecto_{user}.docx", 
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            else:
                st.write("Fases en construcción para este departamento...")
