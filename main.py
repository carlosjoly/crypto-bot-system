import time
from apscheduler.schedulers.background import BackgroundScheduler
from src.bot_mercado import executar_analise_mercado
from src.bot_descoberta import executar_descoberta_dinamica

def iniciar_agendador():
    scheduler = BackgroundScheduler()
    
    # Bot de Mercado: executa a cada 15 minutos exatos
    scheduler.add_job(executar_analise_mercado, 'interval', minutes=15)
    
    # Bot de Descoberta: executa a cada 4 horas exatas
    scheduler.add_job(executar_descoberta_dinamica, 'interval', hours=4)
    
    scheduler.start()
    print("🚀 Agendador interno iniciado com sucesso! Monitorando tarefas...")

    # Executa uma vez imediatamente ao ligar o servidor
    print("▶️ Executando varreduras iniciais...")
    executar_analise_mercado()
    executar_descoberta_dinamica()

    # Mantém o processo Python ativo na nuvem
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    iniciar_agendador()
