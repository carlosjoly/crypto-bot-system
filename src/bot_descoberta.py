import requests
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.telegram_alerter import enviar_alerta_telegram

def verificar_seguranca_goplus(chain_id: str, token_address: str):
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

def executar_descoberta():
    print("[{}] Executando Bot de Descoberta e Segurança...".format(datetime.now()))
    alvos_exemplo = [
        {
            "nome": "Tether USD (USDT - Exemplo)", 
            "chain_id": "1", 
            "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
            "utilidade": 25, "equipa": 15, "tokenomics": 20, "adocao": 15, "social": 10
        }
    ]
    
    for alvo in alvos_exemplo:
        status_seguranca, detalhes_risco = verificar_seguranca_goplus(alvo["chain_id"], alvo["address"])
        pontos_seguranca = 15 if status_seguranca == "SEGURO" else 0
        pontuacao_total = (
            alvo.get("utilidade", 0) + alvo.get("equipa", 0) + 
            alvo.get("tokenomics", 0) + alvo.get("adocao", 0) + 
            alvo.get("social", 0) + pontos_seguranca
        )
        riscos_texto = "\n".join([f"• {r}" for r in detalhes_risco]) if detalhes_risco else "• Nenhum risco crítico detetado no contrato."
        
        mensagem = (
            f"🔍 *RELATÓRIO DE DESCOBERTA & SEGURANÇA (GoPlus API)*\n\n"
            f"• *Projeto:* `{alvo['nome']}`\n"
            f"• *Avaliação Total:* `{pontuacao_total}/100`\n"
            f"• *Estado GoPlus:* `{status_seguranca}`\n\n"
            f"*Análise de Riscos do Contrato:*\n{riscos_texto}\n\n"
            f"_Próximo passo: Validação manual antes de considerar qualquer swing trade._"
        )
        enviar_alerta_telegram(mensagem)
        print(f"Alerta enviado para: {alvo['nome']}")

if __name__ == "__main__":
    executar_descoberta()