import ccxt
import requests
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.telegram_alerter import enviar_alerta_telegram

def verificar_seguranca_goplus(chain_id: str, token_address: str):
    """Consulta a API da GoPlus para validar riscos do contrato."""
    url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}"
    params = {"contract_addresses": token_address}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            if token_address.lower() in result:
                token_data = result[token_address.lower()]
                is_honeypot = token_data.get("is_honeypot", "0") == "1"
                buy_tax = float(token_data.get("buy_tax", 0)) * 100
                sell_tax = float(token_data.get("sell_tax", 0)) * 100
                can_take_back_ownership = token_data.get("can_take_back_ownership", "0") == "1"
                
                riscos_encontrados = []
                if is_honeypot:
                    riscos_encontrados.append("⚠️ **ALERTA CRÍTICO: Honeypot detetado!**")
                if buy_tax > 10 or sell_tax > 10:
                    riscos_encontrados.append(f"⚠️ Taxas elevadas (Compra: {buy_tax}%, Venda: {sell_tax}%)")
                if can_take_back_ownership:
                    riscos_encontrados.append("⚠️ O criador pode recuperar a propriedade do contrato.")
                    
                status_seguranca = "SEGURO" if not riscos_encontrados else "ALTO RISCO"
                return status_seguranca, riscos_encontrados
        return "PENDENTE / DESCONHECIDO", ["Não foi possível validar automaticamente ou contrato não encontrado."]
    except Exception as e:
        print(f"[Erro na API GoPlus]: {e}")
        return "ERRO NA CONSULTA", [str(e)]

def executar_descoberta_dinamica():
    print("[{}] Executando Bot de Descoberta Avançado via CCXT...".format(datetime.now()))
    
    try:
        # Substituído para KuCoin de forma a evitar restrições geográficas de IP em nuvem (GitHub Actions)
        exchange = ccxt.kucoin({
            'enableRateLimit': True,
        })
        
        markets = exchange.fetch_markets()
        
        # Filtra apenas pares ativos em USDT
        pares_usdt = [m for m in markets if m['quote'] == 'USDT' and m['active']]
        
        # OTIMIZAÇÃO PARA O WORKER: Analisa apenas os primeiros 5 ativos 
        alvos_para_analise = pares_usdt[:5]
        
        for mercado in alvos_para_analise:
            simbolo = mercado['symbol'] # Ex: 'BTC/USDT'
            print(f"Analisando mercado: {simbolo}")
            
            ticker = exchange.fetch_ticker(simbolo)
            volume_24h = ticker.get('quoteVolume', 0)
            
            pontos_adocao = 15 if volume_24h > 1000000 else 5
            
            # Definição de rede e endereço (Exemplo para Ethereum/Outras redes mapeadas)
            chain_id = "1" 
            contract_address = mercado.get('info', {}).get('contractAddress', "0xdac17f958d2ee523a2206206994597c13d831ec7")
            
            status_seguranca, detalhes_risco = verificar_seguranca_goplus(chain_id, contract_address)
            pontos_seguranca = 15 if status_seguranca == "SEGURO" else 0
            
            pontuacao_total = 20 + pontos_adocao + pontos_seguranca
            riscos_texto = "\n".join([f"• {r}" for r in detalhes_risco]) if detalhes_risco else "• Nenhum risco crítico detetado."
            
            mensagem = (
                f"🔍 *RELATÓRIO DINÂMICO (GitHub Worker)*\n\n"
                f"• *Par/Ativo:* `{simbolo}`\n"
                f"• *Volume 24h (USDT):* `{volume_24h:,.2f}`\n"
                f"• *Avaliação Total:* `{pontuacao_total}/100`\n"
                f"• *Estado GoPlus:* `{status_seguranca}`\n\n"
                f"*Análise de Riscos:*\n{riscos_texto}\n\n"
                f"_Executado automaticamente via KuCoin (CCXT + GitHub Actions)._"
            )
            enviar_alerta_telegram(mensagem)
            print(f"Alerta enviado para: {simbolo}")
            
    except Exception as e:
        print(f"[Erro Geral na Execução]: {e}")

if __name__ == "__main__":
    executar_descoberta_dinamica()
