import streamlit as st
import pandas as pd
from db import get_connection  # Função para conexão ao banco de dados
from datetime import datetime

def fetch_patients():
    """
    Obtém a lista de pacientes do banco de dados.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nome FROM pacientes;")
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao buscar pacientes: {e}")
        finally:
            conn.close()
    return []

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
                    SELECT nome AS Nome, frequencia AS Frequência, categoria AS Categoria, observacoes AS Observações
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

def fetch_diary_entries(paciente_id):
    """
    Obtém os registros do diário para um paciente específico.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT data, tipo, detalhes, hora
                    FROM diario
                    WHERE paciente_id = %s
                    ORDER BY data, hora;
                    """,
                    (paciente_id,)
                )
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao buscar registros do diário: {e}")
        finally:
            conn.close()
    return []

def view_data():
    """
    Interface para visualizar os dados de pacientes, medicamentos e diário.
    """
    # Buscar pacientes do banco
    pacientes = fetch_patients()
    lista_pacientes = [f"{p['id']} - {p['nome']}" for p in pacientes]

    if lista_pacientes:
        paciente_selecionado = st.selectbox("Selecione o Paciente", lista_pacientes)
        paciente_id = int(paciente_selecionado.split(" - ")[0])

        # Exibir informações do paciente
        st.subheader(f"Informações do Paciente: {paciente_selecionado.split(' - ')[1]}")
        
        # Medicamentos
        st.subheader("Medicamentos")
        medicamentos = fetch_medications(paciente_id)
        if medicamentos:
            medicamentos_df = pd.DataFrame(medicamentos)
            st.dataframe(medicamentos_df)
        else:
            st.warning("Nenhum medicamento cadastrado para este paciente.")

        # Diário
        st.subheader("Diário")
        registros_diario = fetch_diary_entries(paciente_id)
        if registros_diario:
            diario_df = pd.DataFrame(registros_diario)
            st.dataframe(diario_df)
        else:
            st.warning("Nenhum registro no diário para este paciente.")
    else:
        st.warning("Nenhum paciente cadastrado.")
