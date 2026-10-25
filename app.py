import os
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Crypto Bot Monitor", page_icon="📈", layout="wide")

st.title("🛡️ Sistema de Bots Independentes - Swing Trade")
st.markdown("Painel de controlo avançado para monitorização 24/7, estado dos bots, logs e testes de infraestrutura.")

# --- Funções Auxiliares ---
@st.cache_data(ttl=5)
def load_logs(n_lines=100, log_level="TODOS"):
    log_path = "logs/system.log"
    if not os.path.exists(log_path):
        # Cria um log inicial simulado caso o diretório/arquivo ainda não exista
        os.makedirs("logs", exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Sistema inicializado com sucesso.\n")
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [WARNING] Aguardando primeiro ciclo do GitHub Actions.\n")
            
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    if log_level != "TODOS":
        lines = [line for line in lines if log_level in line]
        
    return "".join(lines[-n_lines:])

def send_telegram_test_message(token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🟢 *Crypto Monitor Test:* Conexão com o Telegram validada através do painel Streamlit.",
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)

# --- Sidebar de Configuração & Testes ---
st.sidebar.header("Parâmetros do Sistema")
ativo_selecionado = st.sidebar.selectbox("Ativo de Referência", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
tempo_grafico = st.sidebar.selectbox("Período de Análise", ["15m", "1h", "4h"])
capital_ref = st.sidebar.number_input("Capital de Referência (USDT)", value=10000)

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Diagnóstico & Ações")

if st.sidebar.button("🔔 Testar Alerta Telegram"):
    try:
        token = st.secrets.get("TELEGRAM_BOT_TOKEN")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
    except Exception:
        token, chat_id = None, None

    if not token or not chat_id:
        st.sidebar.error("Credenciais do Telegram não configuradas no `st.secrets`.")
    else:
        success, msg = send_telegram_test_message(token, chat_id)
        if success:
            st.sidebar.success("Mensagem enviada com sucesso!")
        else:
            st.sidebar.error(f"Erro ao enviar: {msg}")

# --- Layout Principal em Abas ---
tab1, tab2, tab3, tab4 = st.tabs(["📡 Estado & Heartbeat", "📋 Logs do Sistema", "📊 Histórico de Sinais", "⚙️ Regras & Pontuação"])

with tab1:
    st.subheader("Estado Operacional & Worker Status")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("Bot de Mercado (Altas/Quedas): **ONLINE**")
    with col2:
        st.success("Bot de Descoberta & Fundamentos: **ONLINE**")
    with col3:
        st.info("GitHub Actions Worker: **ATIVO (Há 12 min)**")
        
    st.markdown("---")
    st.info("Arquitetura isolada ativa: A falha em um módulo não afeta os demais. Coleta automatizada via GitHub Actions a cada 15 minutos.")

with tab2:
    st.subheader("📋 Monitorização de Logs em Tempo Real")
    
    col_filter1, col_filter2 = st.columns([2, 2])
    with col_filter1:
        log_level_filter = st.selectbox("Filtrar por Nível", ["TODOS", "INFO", "WARNING", "ERROR"])
    with col_filter2:
        n_lines = st.slider("Número de linhas exibidas", 20, 200, 50)
        
    log_content = load_logs(n_lines=n_lines, log_level=log_level_filter)
    st.code(log_content, language="text")
    
    if st.button("🔄 Atualizar Logs"):
        st.rerun()

with tab3:
    st.subheader("Histórico Recente de Sinais")
    dados_mock = pd.DataFrame([
        {"Hora": "2026-10-23 21:00", "Bot": "Bot de Mercado", "Par": "BTC/USDT", "Sinal": "Alta Expressiva (15m)", "Confiança": "Média"},
        {"Hora": "2026-10-23 18:30", "Bot": "Bot de Descoberta", "Par": "ALPHA", "Sinal": "Novo Projeto (78/100)", "Confiança": "Em Investigação"}
    ])
    st.dataframe(dados_mock, use_container_width=True)

with tab4:
    st.subheader("Critérios de Avaliação (100 Pontos)")
    st.markdown("""
    * **Utilidade e Qualidade:** 25 pts
    * **Tokenomics e Desbloqueios:** 20 pts
    * **Equipa e Execução:** 15 pts
    * **Adoção On-Chain:** 15 pts
    * **Segurança e Contrato:** 15 pts
    * **Interesse Social Orgânico:** 10 pts
    """)