#!/usr/bin/env python
import sys
import warnings
import time
import schedule  # Nueva librería para el cron

from datetime import datetime
from taller_crewai.crew import TallerCrewai #

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd") #

# 1. Creamos una función auxiliar que contiene lo que queremos ejecutar
def tarea_programada():
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year) #[cite: 2]
    }
    print(f"\n--- [CRON] Ejecutando agentes a las {datetime.now().strftime('%H:%M:%S')} ---")
    try:
        TallerCrewai().crew().kickoff(inputs=inputs) #[cite: 2]
        print("--- Tarea finalizada con éxito. Esperando el siguiente ciclo... ---\n")
    except Exception as e:
        print(f"Error en la ejecución: {e}")

def run():
    """
    Run the crew using a cron schedule.
    """
    print("Iniciando el Demonio Cron de CrewAI. Presiona Ctrl+C para detenerlo.")
    
    # 2. Ejecutar la primera vez inmediatamente (opcional)
    tarea_programada()
    
    # 3. Programar la regla del cron (Cada 4 minutos)
    schedule.every(4).minutes.do(tarea_programada)

    # 4. Iniciar el bucle infinito del daemon
    try:
        while True:
            schedule.run_pending()
            time.sleep(1) # Pausa de 1 segundo para no saturar el CPU
    except KeyboardInterrupt:
        print("\nCron detenido por el usuario.")
    except Exception as e:
        raise Exception(f"An error occurred in the cron loop: {e}") #[cite: 2]

# El resto de tus funciones (train, replay, test, run_with_trigger) se quedan exactamente igual.