# Trecho principal integrado ao bot_descoberta.py
from utils.trade_planner import calcular_plano_execucao

# ... dentro do loop de análise de mercado ...
ticker = exchange.fetch_ticker(simbolo)
close_price = ticker.get('last', 0)

# Busca dados de velas recentes (ex: 1h) para calcular volatilidade (ATR simplificado ou desvio)
ohlcv = exchange.fetch_ohlcv(simbolo, timeframe='1h', limit=14)
if ohlcv and len(ohlcv) >= 14:
    # Estimativa de ATR baseada na amplitude média dos últimos candles
    amplitudes = [candle[2] - candle[3] for candle in ohlcv] # High - Low
    atr_aprox = sum(amplitudes) / len(amplitudes)
else:
    atr_aprox = close_price * 0.02 # Fallback de 2% se faltarem dados

plano = calcular_plano_execucao(close_price, atr_aprox)

mensagem = (
    f"🔍 *RELATÓRIO DINÂMICO & PLANO DE TRADE*\n\n"
    f"• *Par/Ativo:* `{simbolo}` | *Preço:* `{close_price:.4f}`\n"
    f"• *Volume 24h (USDT):* `{volume_24h:,.2f}`\n"
    f"• *Avaliação Total:* `{pontuacao_total}/100`\n"
    f"• *Estado GoPlus:* `{status_seguranca}`\n\n"
    f"📋 **Plano de Execução Sugerido:**\n"
    f"• Entrada Técnica: `{close_price:.4f}`\n"
    f"• Stop Loss: `{plano['stop_loss']:.4f}`\n"
    f"• Alvo 1 (Parcial): `{plano['target_1']:.4f}`\n"
    f"• Alvo 2 (Final): `{plano['target_2']:.4f}`\n"
    f"• Risco/Retorno: `1:{plano['rr_ratio']:.1f}`\n\n"
    f"*Análise de Riscos:*\n{riscos_texto}"
)
enviar_alerta_telegram(mensagem)
