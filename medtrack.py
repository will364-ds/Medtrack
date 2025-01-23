import streamlit as st
from diario_diario import daily_diary
from datetime import datetime
from cadastro_paciente import patient_registration
from gerenciamento_medicamentos import medication_management
from visualizar_dados import view_data

# Usuário e senha hardcoded para autenticação
USERS = {
    "admin": "12345",
    "user": "password"
}

def authenticate():
    """
    Exibe a interface de login na barra lateral.
    """
    st.sidebar.title("Autenticação")
    username = st.sidebar.text_input("Usuário", key="login_username")
    password = st.sidebar.text_input("Senha", type="password", key="login_password")

    if st.sidebar.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.sidebar.success(f"Bem-vindo, {username}!")
        else:
            st.sidebar.error("Usuário ou senha incorretos!")

def secure_app():
    """
    Protege a aplicação com autenticação.
    """
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        authenticate()
        return False

    return True

def main():
    """
    Função principal para gerenciar o fluxo do sistema.
    """
    st.set_page_config(page_title="MedTrack", layout="wide")

    if secure_app():
        st.title("MedTrack - Sistema de Gerenciamento de Pacientes (Projeto Cholinho feliz :))")
        
        # Exibir menu lateral
        menu = st.sidebar.selectbox("Menu", ["Cadastro de Paciente", "Gerenciamento de Medicamentos", "Diário Diário", "Visualizar Dados"])

        if menu == "Cadastro de Paciente":
           # st.info("Navegando para Cadastro de Paciente.")
            patient_registration()
        elif menu == "Gerenciamento de Medicamentos":
           # st.info("Navegando para Gerenciamento de Medicamentos.")
            medication_management()
        elif menu == "Diário Diário":
           # st.info("Navegando para Diário Diário.")
            daily_diary()
        elif menu == "Visualizar Dados":
           # st.info("Navegando para Visualizar Dados.")
            view_data()

if __name__ == "__main__":
    main()
