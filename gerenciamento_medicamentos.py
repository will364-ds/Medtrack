import streamlit as st
from db import get_connection  # Função para conectar ao banco de dados

def fetch_doses(paciente_id):
    """
    Obtém medicamentos e suas doses associadas para o paciente.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT m.id AS medicamento_id, m.nome AS medicamento, m.frequencia AS quantidade, d.dose
                    FROM medicamentos m
                    LEFT JOIN doses_tomadas d ON m.id = d.medicamento_id AND d.paciente_id = %s
                    WHERE m.paciente_id = %s;
                    """,
                    (paciente_id, paciente_id)
                )
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao buscar doses: {e}")
        finally:
            conn.close()
    return []

def register_dose(paciente_id, medicamento_id, dose):
    """
    Registra a confirmação de uma dose.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO doses_tomadas (paciente_id, medicamento_id, dose)
                    VALUES (%s, %s, %s);
                    """,
                    (paciente_id, medicamento_id, dose)
                )
                conn.commit()
                st.success("Dose confirmada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao confirmar dose: {e}")
        finally:
            conn.close()

def remove_dose(paciente_id, medicamento_id, dose):
    """
    Remove uma dose ainda não confirmada.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM doses_tomadas
                    WHERE paciente_id = %s AND medicamento_id = %s AND dose = %s;
                    """,
                    (paciente_id, medicamento_id, dose)
                )
                conn.commit()
                st.success("Dose removida com sucesso!")
        except Exception as e:
            st.error(f"Erro ao remover dose: {e}")
        finally:
            conn.close()

def fetch_medications(paciente_id):
    """
    Obtém a lista de medicamentos para um paciente específico.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, nome, frequencia, categoria, observacoes
                    FROM medicamentos
                    WHERE paciente_id = %s;
                    """,
                    (paciente_id,)
                )
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao buscar medicamentos: {e}")
        finally:
            conn.close()
    return []

def save_medication(paciente_id, nome, frequencia, categoria, observacoes):
    """
    Salva um medicamento no banco de dados.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO medicamentos (paciente_id, nome, frequencia, categoria, observacoes)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (paciente_id, nome, frequencia, categoria, observacoes)
                )
                conn.commit()
                st.success(f"Medicamento '{nome}' adicionado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar medicamento: {e}")
        finally:
            conn.close()

def delete_medication(med_id):
    """
    Remove um medicamento do banco de dados.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM medicamentos WHERE id = %s;", (med_id,))
                conn.commit()
                st.success("Medicamento removido com sucesso!")
        except Exception as e:
            st.error(f"Erro ao remover medicamento: {e}")
        finally:
            conn.close()

def medication_management():
    """
    Interface para gerenciar os medicamentos de um paciente.
    """
    # Inicialize 'reload' na sessão se ainda não existir
    if 'reload' not in st.session_state:
        st.session_state['reload'] = False

    # Buscar pacientes
    conn = get_connection()
    pacientes = []
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nome FROM pacientes;")
                pacientes = cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao carregar pacientes: {e}")
        finally:
            conn.close()

    lista_pacientes = [f"{p['id']} - {p['nome']}" for p in pacientes]
    if lista_pacientes:
        paciente_selecionado = st.selectbox("Selecione o Paciente", lista_pacientes)
        paciente_id = int(paciente_selecionado.split(" - ")[0])

        st.subheader("Medicamentos Cadastrados")
        medicamentos = fetch_medications(paciente_id)
        if medicamentos:
            for med in medicamentos:
                with st.expander(f"{med['nome']}"):
                    st.write(f"**Frequência:** {med['frequencia']}")
                    st.write(f"**Categoria:** {med['categoria']}")
                    st.write(f"**Observações:** {med['observacoes']}")

                    # Botão para remover medicamento
                    if st.button("Remover", key=f"remover_{med['id']}"):
                        delete_medication(med['id'])
                        st.session_state['reload'] = True  # Atualiza o estado para recarregar a página

        else:
            st.warning("Nenhum medicamento cadastrado para este paciente.")

        # Formulário para adicionar novos medicamentos
        st.subheader("Adicionar Novo Medicamento")
        with st.form("adicionar_medicamento"):
            nome = st.text_input("Nome do Medicamento")
            frequencia = st.number_input("Frequência (doses por dia)", min_value=1, step=1)
            categoria = st.text_input("Categoria")
            observacoes = st.text_area("Observações")
            submit = st.form_submit_button("Adicionar Medicamento")

            if submit:
                save_medication(paciente_id, nome, frequencia, categoria, observacoes)
                st.session_state['reload'] = True  # Atualiza o estado para recarregar a página

        # Recarga da página
            st.rerun()  # Ou a abordagem alternativa de redirecionamento
    else:
        st.warning("Nenhum paciente cadastrado.")
