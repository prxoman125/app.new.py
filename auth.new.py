import streamlit as st

def check_password(contrasena_correcta="1234"):
    """
    Verifica si el usuario ingresó la contraseña correcta.
    Retorna True si la contraseña es correcta, False si no.
    """
    def password_entered():
        if st.session_state["password_input"] == contrasena_correcta:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]  # Borra la variable de sesión por seguridad
        else:
            st.session_state["password_correct"] = False

    # Si ya se validó antes, no vuelve a pedirla
    if st.session_state.get("password_correct", False):
        return True

    # Pantalla de Login
    st.markdown("## 🔐 Acceso Restringido")
    st.text_input(
        "Por favor, ingresa la contraseña para acceder al simulador:",
        type="password",
        on_change=password_entered,
        key="password_input"
    )

    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")

    return False
