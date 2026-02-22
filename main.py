import streamlit as st
from database import DBManager

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser SIEMPRE la primera instrucción de Streamlit)
st.set_page_config(
    page_title="SGE-CIR Panamá",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. INYECCIÓN DE CSS PARA PERSONALIZACIÓN VISUAL
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    /* Estilo para los títulos principales */
    h1 {
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. IMPORTACIÓN DE MÓDULOS (Después de la configuración de página)
from inventario import ModuloInventario
from cotizaciones import ModuloCotizaciones
from ventas import ModuloVentas
from clientes import ModuloClientes
from contabilidad import ModuloContabilidad
from configuracion import ModuloConfiguracion

# Inicializar manejador de Base de Datos
db = DBManager()

# 4. INICIALIZACIÓN DE SESSION STATE (Gestión de sesión)
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'rol' not in st.session_state:
    st.session_state.rol = None

# --- LÓGICA DE INTERFAZ ---

if not st.session_state.autenticado:
    # --- PANTALLA DE LOGIN ---
    st.markdown("<h1 style='text-align: center; color: #707070; font-weight: bold;'>🤖 CIR PANAMÁ</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #A0A0A0; font-family: sans-serif; font-weight: normal;'>Sistema de Gestión Empresarial</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #707070; font-weight: bold;'>👋 Bienvenidos</h2>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submit:
                # Consulta a la tabla perfiles mediante el DBManager
                res = db.fetch("perfiles")
                user = next((u for u in res if u['usuario'] == usuario and u['clave'] == clave), None)
                
                if user:
                    st.session_state.autenticado = True
                    st.session_state.user_data = user
                    st.session_state.rol = user.get('rol', 'usuario')
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas o usuario no existe.")

else:
    # --- INTERFAZ DEL SISTEMA PRINCIPAL (AUTENTICADO) ---
    with st.sidebar:
        st.markdown(f"<h2 style='color: #707070; font-weight: bold;'>🏗️ CIR PANAMÁ</h2>", unsafe_allow_html=True)
        
        u_name = st.session_state.user_data.get('usuario', 'N/A')
        u_rol = st.session_state.rol
        
        st.write(f"Usuario: **{u_name}**")
        st.write(f"Permisos: `{u_rol}`")
        st.divider()
        
        # Menú dinámico según el rol
        opciones = ["📦 Inventario", "📄 Cotizaciones", "🛒 Ventas", "👥 Clientes", "💰 Contabilidad"]
        
        # Solo el rol master_it puede ver la configuración técnica
        if u_rol == "master_it":
            opciones.append("⚙️ Configuración")
            
        choice = st.radio("Navegación", opciones)
        
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.user_data = None
            st.session_state.rol = None
            st.rerun()

    # --- ENRUTADOR DE MÓDULOS (Renderizado de contenido) ---
    if choice == "📦 Inventario":
        ModuloInventario(db).render()
    elif choice == "📄 Cotizaciones":
        ModuloCotizaciones(db).render()
    elif choice == "🛒 Ventas":
        ModuloVentas(db).render()
    elif choice == "👥 Clientes":
        ModuloClientes(db).render()
    elif choice == "💰 Contabilidad":
        ModuloContabilidad(db).render()
    elif choice == "⚙️ Configuración":
        ModuloConfiguracion(db).render()