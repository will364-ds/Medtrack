import streamlit as st
from db import get_connection  # Função para conectar ao banco

def save_patient(nome, idade, sexo, altura, peso):
    """
    Salva um paciente no banco de dados PostgreSQL.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO pacientes (nome, idade, sexo, altura, peso)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (nome, idade, sexo, altura, peso)
                )
                conn.commit()
                st.success(f"Paciente '{nome}' cadastrado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar paciente: {e}")
        finally:
            conn.close()

def update_patient(paciente_id, nome, idade, sexo, altura, peso):
    """
    Atualiza os dados de um paciente no banco de dados PostgreSQL.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE pacientes
                    SET nome = %s, idade = %s, sexo = %s, altura = %s, peso = %s
                    WHERE id = %s;
                    """,
                    (nome, idade, sexo, altura, peso, paciente_id)
                )
                conn.commit()
                st.success(f"Paciente '{nome}' atualizado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao atualizar paciente: {e}")
        finally:
            conn.close()

def delete_patient(paciente_id):
    """
    Remove um paciente do banco de dados PostgreSQL.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM pacientes WHERE id = %s;", (paciente_id,))
                conn.commit()
                st.success(f"Paciente removido com sucesso!")
        except Exception as e:
            st.error(f"Erro ao remover paciente: {e}")
        finally:
            conn.close()

def fetch_patients():
    """
    Obtém a lista de pacientes do banco de dados PostgreSQL.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nome, idade, sexo, altura, peso FROM pacientes;")
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao buscar pacientes: {e}")
        finally:
            conn.close()
    return []

def patient_registration():
    """
    Interface para cadastro, edição e remoção de pacientes.
    """
    st.header("Cadastro de Pacientes")

    # Exibe a lista de pacientes
    pacientes = fetch_patients()
    if pacientes:
        st.subheader("Pacientes Cadastrados")
        for paciente in pacientes:
            with st.expander(f"{paciente['nome']}"):
                st.write(f"**Idade:** {paciente['idade']}")
                st.write(f"**Sexo:** {paciente['sexo']}")
                st.write(f"**Altura:** {paciente['altura']} cm")
                st.write(f"**Peso:** {paciente['peso']} kg")

        # Botão para editar paciente
        if st.button("Editar", key=f"editar_{paciente['id']}"):
            with st.form(f"editar_form_{paciente['id']}"):
                nome = st.text_input("Nome", value=paciente['nome'])
                idade = st.number_input("Idade", min_value=0, step=1, value=paciente['idade'])
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"], index=["Masculino", "Feminino", "Outro"].index(paciente['sexo']))
                altura = st.number_input("Altura (cm)", min_value=0.0, step=0.1, value=float(paciente['altura']))
                peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1, value=float(paciente['peso']))
                submit = st.form_submit_button("Salvar Alterações")

                if submit:
                    if not nome.strip():
                        st.error("O campo 'Nome' é obrigatório.")
                    else:
                        update_patient(paciente['id'], nome, idade, sexo, altura, peso)
                        st.rerun()

        # Botão para remover paciente
        remove_key = f"remover_{paciente['id']}"
        confirm_key = f"confirmar_remocao_{paciente['id']}"
        
        # Exibir botão de remoção
        if st.button("Remover", key=remove_key):
            st.session_state[confirm_key] = True  # Ativa a confirmação

        # Exibir confirmação se o botão de remoção foi clicado
        if st.session_state.get(confirm_key, False):
            st.warning(f"Você tem certeza de que deseja remover o paciente '{paciente['nome']}'?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sim, remover", key=f"confirmar_{paciente['id']}"):
                    delete_patient(paciente['id'])
                    st.session_state[confirm_key] = False  # Reseta a confirmação
            with col2:
                if st.button("Cancelar", key=f"cancelar_{paciente['id']}"):
                    st.session_state[confirm_key] = False  # Reseta a confirmação

    # Formulário para adicionar novo paciente
    st.subheader("Adicionar Novo Paciente")
    with st.form("cadastro_paciente"):
        nome = st.text_input("Nome")
        idade = st.number_input("Idade", min_value=0, step=1)
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
        altura = st.number_input("Altura (cm)", min_value=0.0, step=0.1)
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
        submit = st.form_submit_button("Cadastrar")

        if submit:
            if not nome.strip():
                st.error("O campo 'Nome' é obrigatório.")
            else:
                save_patient(nome, idade, sexo, altura, peso)
                st.rerun()
