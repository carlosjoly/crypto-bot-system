# Atualização na estrutura do bot_mercado.py
exchange = ccxt.kucoin({
    'enableRateLimit': True,
})

markets = exchange.fetch_markets()
pares_alvo = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'ADA/USDT']

for simbolo in pares_alvo:
    ticker = exchange.fetch_ticker(simbolo)
    preco_atual = ticker.get('last', 0)
    variacao = ticker.get('percentage', 0) or 0
    
    if abs(variacao) >= 3.0:
        # Cálculo do plano de execução via ATR nas velas de 4h
        ohlcv = exchange.fetch_ohlcv(simbolo, timeframe='4h', limit=14)
        amplitudes = [c[2] - c[3] for c in ohlcv]
        atr = sum(amplitudes) / len(amplitudes) if amplitudes else preco_atual * 0.02
        
        plano = calcular_plano_execucao(preco_atual, atr)
        
        tipo_movimento = "🚀 ALTA EXPRESSIVA" if variacao > 0 else "🔻 QUEDA EXPRESSIVA"
        mensagem = (
            f"*{tipo_movimento} (Bot de Mercado)*\n\n"
            f"• *Par:* `{symbol}` | *Preço:* `{preco_atual:.4f}`\n"
            f"• *Variação (24h):* `{variacao:.2f}%`\n\n"
            f"📋 **Plano de Execução Sugerido:**\n"
            f"• Entrada: `{preco_atual:.4f}`\n"
            f"• Stop Loss: `{plano['stop_loss']:.4f}`\n"
            f"• Alvo 1: `{plano['target_1']:.4f}`\n"
            f"• Alvo 2: `{plano['target_2']:.4f}`\n"
            f"• Risco/Retorno: `1:{plano['rr_ratio']:.1f}`"
        )
        enviar_alerta_telegram(mensagem)
