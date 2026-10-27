# utils/trade_planner.py
def calcular_plano_execucao(close_price: float, atr: float, multiplier_sl=2.0, multiplier_t1=2.0, multiplier_t2=4.0):
    """Calcula os níveis técnicos de entrada, stop loss e alvos com base na volatilidade (ATR)."""
    stop_loss = close_price - (multiplier_sl * atr)
    target_1 = close_price + (multiplier_t1 * atr)
    target_2 = close_price + (multiplier_t2 * atr)
    
    risco = close_price - stop_loss
    retorno = target_1 - close_price
    rr_ratio = retorno / risco if risco > 0 else 0
    
    return {
        "stop_loss": stop_loss,
        "target_1": target_1,
        "target_2": target_2,
        "rr_ratio": rr_ratio
    }
