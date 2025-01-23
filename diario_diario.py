import psycopg2
from datetime import datetime, time
import streamlit as st
from db import get_connection

def save_diary_entry(paciente_id, tipo, data_hora, detalhes):
    """
    Salva uma entrada no diário do banco de dados.
    """
    if not tipo.strip() or not detalhes.strip():
        st.error("Os campos 'Tipo' e 'Detalhes' são obrigatórios.")
        return

    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO diario (paciente_id, data, tipo, detalhes, hora)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (paciente_id, data_hora.date(), tipo, detalhes, data_hora.time())
                )
                conn.commit()
                st.success(f"Registro '{tipo}' salvo com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar registro no diário: {e}")
        finally:
            conn.close()

def fetch_diary_entries(paciente_id, data):
    """
    Busca entradas do diário no banco de dados.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT tipo, data, hora, detalhes
                    FROM diario
                    WHERE paciente_id = %s AND data = %s;
                    """,
                    (paciente_id, data)
                )
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao buscar registros do diário: {e}")
        finally:
            conn.close()
    return []

def fetch_doses(paciente_id):
    """
    Busca medicamentos e suas doses associadas para o paciente.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT m.id AS medicamento_id, m.nome AS medicamento, m.frequencia AS quantidade
                    FROM medicamentos m
                    WHERE m.paciente_id = %s;
                    """,
                    (paciente_id,)
                )
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Erro ao buscar doses: {e}")
        finally:
            conn.close()
    return []

def register_dose(paciente_id, medicamento_id, dose, hora):
    """
    Registra a confirmação de uma dose com o horário especificado.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO doses_tomadas (paciente_id, medicamento_id, dose, data_hora)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (paciente_id, medicamento_id, dose, hora)
                )
                conn.commit()
                st.success("Dose confirmada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao confirmar dose: {e}")
        finally:
            conn.close()

def delete_dose(paciente_id, medicamento_id, dose):
    """
    Remove uma dose confirmada no banco de dados.
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

def delete_diary_entry(paciente_id, data, hora):
    """
    Remove uma entrada do diário do banco de dados.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM diario
                    WHERE paciente_id = %s AND data = %s AND hora = %s;
                    """,
                    (paciente_id, data, hora)
                )
                conn.commit()
                st.success("Registro do diário removido com sucesso!")
        except Exception as e:
            st.error(f"Erro ao remover registro do diário: {e}")
        finally:
            conn.close()

def daily_diary():
    """
    Interface para gerenciamento de diário e doses de medicamentos.
    """
    # Buscar pacientes
    conn = get_connection()
    pacientes = []
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome FROM pacientes;")
            pacientes = cursor.fetchall()
        conn.close()

    lista_pacientes = [f"{p['id']} - {p['nome']}" for p in pacientes]
    if lista_pacientes:
        paciente_selecionado = st.selectbox("Selecione o Paciente", lista_pacientes)
        paciente_id = int(paciente_selecionado.split(" - ")[0])
        data_selecionada = st.date_input("Selecione a Data", value=datetime.now().date())

        # Gerenciamento de Doses
        st.subheader("Gerenciamento de Doses de Medicamentos")
        doses = fetch_doses(paciente_id)

        for dose in doses:
            medicamento_id = dose['medicamento_id']
            medicamento = dose['medicamento']
            quantidade = dose['quantidade']

            st.markdown(f"### Medicamento: {medicamento}")
            for d in range(1, quantidade + 1):
                dose_key = f"dose_{medicamento_id}_{d}"
                hora_confirmada = st.session_state.get(f"dose_confirmada_{dose_key}")

                col1, col2 = st.columns([0.8, 0.2])

                with col1:
                    if hora_confirmada:
                        st.markdown(f"**Dose {d} - Administrada às {hora_confirmada.strftime('%H:%M')}**")
                    else:
                        hora_especificada = st.time_input(
                            f"Horário para Dose {d}",
                            key=f"hora_{medicamento_id}_{d}"
                        )
                        if st.button(f"Confirmar Horário para Dose {d}", key=f"confirmar_hora_{medicamento_id}_{d}"):
                            data_hora = datetime.combine(data_selecionada, hora_especificada)
                            register_dose(paciente_id, medicamento_id, d, data_hora)
                            st.session_state[f"dose_confirmada_{dose_key}"] = data_hora
                            st.rerun()

                with col2:
                    if st.button("Remover Dose", key=f"remover_{medicamento_id}_{d}"):
                        delete_dose(paciente_id, medicamento_id, d)
                        if f"dose_confirmada_{dose_key}" in st.session_state:
                            del st.session_state[f"dose_confirmada_{dose_key}"]
                        st.rerun()

        # Exibir registros do diário
        st.subheader(f"Registros do Diário ({data_selecionada})")
        registros = fetch_diary_entries(paciente_id, data_selecionada)
        for registro in registros:
            with st.expander(f"{registro['tipo']} - {registro['hora']}"):
                st.write(f"**Detalhes:** {registro['detalhes']}")
                if st.button("Remover", key=f"remover_diario_{registro['hora']}"):
                    delete_diary_entry(paciente_id, registro['data'], registro['hora'])
                    st.rerun()

        # Formulário para novos registros
        st.subheader("Adicionar Novo Registro")
        tipo = st.selectbox("Tipo", ["Fisiologia", "Sinais Vitais", "Ocorrência", "Alimentação", "Líquidos"])

        detalhes = ""
        data_hora = datetime.now()

        if tipo == "Fisiologia":
            subtipo = st.selectbox("Subtipo", ["Urina", "Fezes"], key="fisiologia_subtipo")
            quantidade = st.text_input("Quantidade", key="fisiologia_quantidade")
            hora = st.time_input("Hora", value=datetime.now().time(), key="fisiologia_hora")
            detalhes = f"Subtipo: {subtipo}, Quantidade: {quantidade}, Hora: {hora}"

        elif tipo == "Sinais Vitais":
            o2 = st.text_input("O2", key="sinais_vitais_o2")
            pa = st.text_input("PA", key="sinais_vitais_pa")
            hr = st.text_input("HR", key="sinais_vitais_hr")
            temp = st.text_input("TEMP", key="sinais_vitais_temp")
            glic = st.text_input("GLIC", key="sinais_vitais_glic")
            detalhes = f"O2: {o2}, PA: {pa}, HR: {hr}, TEMP: {temp}, GLIC: {glic}"

        elif tipo == "Ocorrência":
            subtipo = st.selectbox("Subtipo", ["Dor", "Confusão", "Falta de Ar", "Mal Estar", "Desmaio", "Tontura"], key="ocorrencia_subtipo")
            if subtipo == "Dor":
                hora_inicial = st.time_input("Hora Inicial", key="ocorrencia_dor_hora_inicial")
                hora_final = st.time_input("Hora Final", key="ocorrencia_dor_hora_final")
                intensidade = st.slider("Intensidade (0-10)", 0, 10, key="ocorrencia_dor_intensidade")
                observacao = st.text_area("Observação", key="ocorrencia_dor_observacao")
                detalhes = f"Subtipo: {subtipo}, Hora Inicial: {hora_inicial}, Hora Final: {hora_final}, Intensidade: {intensidade}, Observação: {observacao}"
            elif subtipo in ["Falta de Ar", "Mal Estar", "Desmaio", "Tontura"]:
                hora_inicial = st.time_input("Hora Inicial", key=f"{subtipo}_hora_inicial")
                hora_final = st.time_input("Hora Final", key=f"{subtipo}_hora_final")
                observacao = st.text_area("Observação", key=f"{subtipo}_observacao")
                detalhes = f"Subtipo: {subtipo}, Hora Inicial: {hora_inicial}, Hora Final: {hora_final}, Observação: {observacao}"

        elif tipo == "Alimentação":
            refeicao = st.selectbox("Refeição", ["Café", "Almoço", "Jantar", "Chá da Tarde"], key="alimentacao_refeicao")
            hora_inicial = st.time_input("Hora Inicial", key="alimentacao_hora_inicial")
            hora_final = st.time_input("Hora Final", key="alimentacao_hora_final")
            quantidade_aprox = st.text_input("Quantidade Aproximada", key="alimentacao_quantidade")
            observacao = st.text_area("Observação", key="alimentacao_observacao")
            detalhes = f"Refeição: {refeicao}, Hora Inicial: {hora_inicial}, Hora Final: {hora_final}, Quantidade: {quantidade_aprox}, Observação: {observacao}"

        elif tipo == "Líquidos":
            liquido = st.selectbox("Líquido", ["Água", "Café", "Isotônico", "Soro", "Chá"], key="liquidos_tipo")
            hora_inicial = st.time_input("Hora Inicial", key="liquidos_hora_inicial")
            hora_final = st.time_input("Hora Final", key="liquidos_hora_final")
            quantidade = st.text_input("Quantidade (ml)", key="liquidos_quantidade")
            observacao = st.text_area("Observação", key="liquidos_observacao")
            detalhes = f"Líquido: {liquido}, Hora Inicial: {hora_inicial}, Hora Final: {hora_final}, Quantidade: {quantidade}, Observação: {observacao}"

        if st.button("Salvar Registro"):
            save_diary_entry(paciente_id, tipo, data_hora, detalhes)
            st.rerun()
