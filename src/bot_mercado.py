import ccxt
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.telegram_alerter import enviar_alerta_telegram

def executar_analise_mercado():
    print("[{}] Executando varredura do Bot de Mercado (via CoinGecko)...".format(datetime.now()))
    
    # Utiliza a CoinGecko para evitar bloqueios de IP (Erro 451) em servidores de nuvem
    exchange = ccxt.coingecko({
        'enableRateLimit': True,
    })
    
    # Mapeamento de símbolos compatíveis com a CoinGecko no CCXT
    symbols_map = {
        'BTC/USDT': 'bitcoin/usdt',
        'ETH/USDT': 'ethereum/usdt',
        'SOL/USDT': 'solana/usdt',
        'BNB/USDT': 'binancecoin/usdt',
        'ADA/USDT': 'cardano/usdt',
        'XRP/USDT': 'ripple/usdt',
        'AVAX/USDT': 'avalanche-2/usdt'
    }
    
    for symbol, cg_id in symbols_map.items():
        try:
            # Como a Coingecko fornece dados agregados, buscamos o ticker atual
            ticker = exchange.fetch_ticker(cg_id)
            preco_atual = ticker.get('last', 0)
            variacao = ticker.get('percentage', 0) or 0 # Variação de 24h na Coingecko
            
            print(f"Ativo: {symbol} | Preço: {preco_atual} | Variação 24h: {variacao}%")
            
            # Condição de alerta (ajustada para variação percentual disponível)
            if abs(variacao) >= 3.0: # Limiar de 3% no acumulado para exemplo
                tipo_movimento = "🚀 ALTA EXPRESSIVA (24h)" if variacao > 0 else "🔻 QUEDA EXPRESSIVA (24h)"
                mensagem = (
                    f"*{tipo_movimento} (Bot de Mercado)*\n\n"
                    f"• *Par:* `{symbol}`\n"
                    f"• *Preço Atual:* `{preco_atual}`\n"
                    f"• *Variação:* `{variacao:.2f}%`\n"
                    f"• *Horário:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
                    f"_Fonte: CoinGecko API (Cloud-friendly)_"
                )
                enviar_alerta_telegram(mensagem)
                print(f"Alerta enviado para {symbol}: variação de {variacao:.2f}%")
                
        except Exception as e:
            print(f"[Erro ao analisar {symbol} via CoinGecko]: {e}")

if __name__ == "__main__":
    executar_analise_mercado()