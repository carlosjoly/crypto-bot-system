import os
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Crypto Bot Monitor", page_icon="📈", layout="wide")

st.title("🛡️ Sistema de Bots Independentes - Swing Trade")
st.markdown("Painel de controlo avançado para monitorização 24/7, controlo de workers, logs em tempo real e testes.")

# --- Função para Disparar GitHub Actions via API ---
def disparar_github_workflow(workflow_filename):
    try:
        repo = st.secrets.get("GITHUB_REPO") 
        token = st.secrets.get("GITHUB_TOKEN") 
        
        if not repo or not token:
            return False, "Configurações GITHUB_REPO ou GITHUB_TOKEN em falta no st.secrets."
            
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_filename}/dispatches"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        payload = {"ref": "main"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 204:
            return True, "Workflow disparado com sucesso no GitHub!"
        else:
            return False, f"Erro da API GitHub ({response.status_code}): {response.text}"
    except Exception as e:
        return False, str(e)

# --- Funções Auxiliares de Logs ---
@st.cache_data(ttl=2)
def load_logs(n_lines=100, log_level="TODOS"):
    log_path = "logs/system.log"
    if not os.path.exists(log_path):
        os.makedirs("logs", exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Sistema inicializado.\n")
            
    with open(log_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        
    if log_level != "TODOS":
        lines = [line for line in lines if log_level in line]
        
    return "\n".join(lines[-n_lines:])

def limpar_logs():
    log_path = "logs/system.log"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Logs limpos manualmente pelo painel Streamlit.\n")
    st.cache_data.clear()

def send_telegram_test_message(token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🟢 *Crypto Monitor Test:* Conexão com o Telegram validada com sucesso.",
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)

# --- Sidebar de Configuração & Ações ---
st.sidebar.header("Parâmetros do Sistema")
ativo_selecionado = st.sidebar.selectbox("Ativo de Referência", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
tempo_grafico = st.sidebar.selectbox("Período de Análise", ["15m", "1h", "4h"])
capital_ref = st.sidebar.number_input("Capital de Referência (USDT)", value=10000)

st.sidebar.markdown("---")
st.sidebar.subheader("🕹️ Controlo Manual de Workers")

if st.sidebar.button("🚀 Executar Market Bot Agora"):
    # Certifique-se de usar .yml ou .yaml conforme o ficheiro criado no repositório
    success, msg = disparar_github_workflow("market_worker.yml")
    if success:
        st.sidebar.success(msg)
    else:
        st.sidebar.error(msg)

if st.sidebar.button("🔍 Executar Discovery Bot Agora"):
    success, msg = disparar_github_workflow("discovery_worker.yml")
    if success:
        st.sidebar.success(msg)
    else:
        st.sidebar.error(msg)

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Diagnóstico & Testes")

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
tab1, tab2, tab3, tab4 = st.tabs(["📡 Estado & Workers", "📋 Logs do Sistema", "📊 Histórico de Sinais", "⚙️ Regras & Pontuação"])

with tab1:
    st.subheader("Estado Operacional dos Workers Independentes")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("Market Bot (15m): **ONLINE**")
    with col2:
        st.success("Discovery Bot (4h): **ONLINE**")
    with col3:
        st.info("Streamlit Cloud: **SINCRONIZADO**")
        
    st.markdown("---")
    st.info("Arquitetura dividida ativa: O *Market Bot Worker* roda a cada 15 minutos e o *Discovery Bot Worker* executa a cada 4 horas de forma isolada.")

with tab2:
    st.subheader("📋 Monitorização de Logs em Tempo Real")
    
    col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 1])
    with col_filter1:
        log_level_filter = st.selectbox("Filtrar por Nível", ["TODOS", "INFO", "WARNING", "ERROR"])
    with col_filter2:
        n_lines = st.slider("Número de linhas exibidas", 20, 200, 50)
    with col_filter3:
        st.write("")
        st.write("")
        if st.button("🗑️ Limpar Logs"):
            limpar_logs()
            st.success("Logs limpos com sucesso!")
            st.rerun()
        
    log_content = load_logs(n_lines=n_lines, log_level=log_level_filter)
    st.code(log_content, language="text")
    
    if st.button("🔄 Atualizar Visualização"):
        st.rerun()

with tab3:
    st.subheader("Histórico Recente de Sinais")
    dados_mock = pd.DataFrame([
        {"Hora": "2026-10-25 15:59", "Bot": "Market Bot", "Par": "BTC/USDT", "Sinal": "Varredura CoinGecko Concluída", "Confiança": "Técnica"},
        {"Hora": "2026-10-25 15:39", "Bot": "Discovery Bot", "Par": "USDT", "Sinal": "Relatório GoPlus (100/100)", "Confiança": "Seguro"}
    ])
    # Substituído use_container_width por width='stretch' para evitar avisos de depreciação
    st.dataframe(dados_mock, width='stretch')

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