#!/usr/bin/env python
import sys
import warnings
import time
import schedule  # librería para el cron

from datetime import datetime
from taller_crewai.crew import TallerCrewai #

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd") #

# función auxiliar que contiene lo que queremos ejecutar
def tarea_programada():
    inputs = {
        'topic': 'Minecraft nueva Dimensión',
        'current_year': str(datetime.now().year)
    }
    print(f"\n--- [CRON] Ejecutando agentes a las {datetime.now().strftime('%H:%M:%S')} ---")
    try:
        TallerCrewai().crew().kickoff(inputs=inputs) 
        print("--- Tarea finalizada con éxito. Esperando el siguiente ciclo... ---\n")
    except Exception as e:
        print(f"Error en la ejecución: {e}")

def run():
    """
    Run the crew using a cron schedule.
    """
    print("Iniciando el Demonio Cron de CrewAI. Presiona Ctrl+C para detenerlo.")
    
    # ejecutar la primera vez inmediatamente
    tarea_programada()
    
    # Programar la regla del cron (Cada 8 minutos)
    schedule.every(8).minutes.do(tarea_programada)

    # Iniciar el bucle infinito del daemon
    try:
        while True:
            schedule.run_pending()
            time.sleep(1) # Pausa de 1 segundo para no saturar el CPU
    except KeyboardInterrupt:
        print("\nCron detenido por el usuario.")
    except Exception as e:
        raise Exception(f"An error occurred in the cron loop: {e}") #[cite: 2]     

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "Minecraft nueva Dimensión",
        'current_year': str(datetime.now().year)
    }
    try:
        TallerCrewai().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        TallerCrewai().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "Minecraft nueva Dimensión",
        "current_year": str(datetime.now().year)
    }

    try:
        TallerCrewai().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = TallerCrewai().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
