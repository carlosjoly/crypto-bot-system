import ccxt
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.telegram_alerter import enviar_alerta_telegram

def executar_analise_mercado():
    print("[{}] Executando varredura do Bot de Mercado...".format(datetime.now()))
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'ADA/USDT', 'XRP/USDT', 'AVAX/USDT']
    
    for symbol in symbols:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=50)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            df['change_15m'] = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
            df['volume_medio'] = df['volume'].rolling(window=20).mean()
            is_volume_alto = df['volume'].iloc[-1] > (df['volume_medio'].iloc[-1] * 2.0)
            
            preco_atual = df['close'].iloc[-1]
            variacao = df['change_15m'].iloc[-1]
            
            if abs(variacao) >= 1.5 and is_volume_alto:
                tipo_movimento = "🚀 ALTA EXPRESSIVA" if variacao > 0 else "🔻 QUEDA EXPRESSIVA / SUPORTE"
                mensagem = (
                    f"*{tipo_movimento} (Bot de Mercado)*\n\n"
                    f"• *Par:* `{symbol}`\n"
                    f"• *Preço Atual:* `{preco_atual}`\n"
                    f"• *Variação (15m):* `{variacao:.2f}%`\n"
                    f"• *Volume:* Anormal (Acima de 2x da média)\n"
                    f"• *Horário:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
                    f"_Aviso: Apenas alerta técnico para análise manual._"
                )
                enviar_alerta_telegram(mensagem)
                print(f"Alerta enviado para {symbol}: variação de {variacao:.2f}%")
        except Exception as e:
            print(f"[Erro ao analisar {symbol}]: {e}")

if __name__ == "__main__":
    executar_analise_mercado()