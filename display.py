import time, sys, os, subprocess, signal
import sysv_ipc 

MQ_KEY = 12345

def main():
    # 1. Configuration Initiale
    try:
        n_preys = int(input("Nombre de proies initiales : "))
        n_preds = int(input("Nombre de prédateurs initiaux : "))
    except: return

    # 2. Lancement du Processus Environnement
    env_p = subprocess.Popen([sys.executable, "env.py"])
    time.sleep(2) # Attente nécessaire pour l'initialisation du serveur

    # Connexion à la Message Queue créée par l'Env
    try:
        mq = sysv_ipc.MessageQueue(MQ_KEY)
    except:
        print("Erreur: Impossible de se connecter à la MessageQueue.")
        os.kill(env_p.pid, 9)
        return
    
    # 3. Lancement des populations initiales
    for _ in range(n_preys): subprocess.Popen([sys.executable, "prey.py"])
    for _ in range(n_preds): subprocess.Popen([sys.executable, "predator.py"])

    # 4. Thread Contrôleur du Climat
    # Envoie un signal SIGUSR1 au processus Env pour alterner Sécheresse/Normal
    def climate_controller(pid_env):
        while True:
            time.sleep(10)
            try: os.kill(pid_env, signal.SIGUSR1)
            except: break
            time.sleep(5)
            try: os.kill(pid_env, signal.SIGUSR1)
            except: break
             
    import threading
    threading.Thread(target=climate_controller, args=(env_p.pid,), daemon=True).start()

    print("Démarrage de l'affichage via MQ...")
    life_started = False 

    # 5. Boucle d'Affichage et de Surveillance
    try:
        while True:
            try:
                # Lecture bloquante de la MQ
                message, t = mq.receive(type=1) 
                data = message.decode().split('|')
                
                # Parsing des données
                grass = int(data[0])
                preys = int(data[1])
                active = int(data[2])
                preds = int(data[3])
                is_drought = bool(int(data[4]))

                # Rendu Interface
                os.system('clear' if os.name == 'posix' else 'cls')
                print(f"--- SIMULATION ---")
                print(f"Météo: {'SÉCHERESSE !!!' if is_drought else 'Temps Normal'}")
                print(f"Herbe: {grass}")
                print(f"Proies: {preys} (Actives: {active})")
                print(f"Loups:  {preds}")
                print("------------------------------------------")
                print("(Appuyez sur Ctrl+C pour arrêter)")
                
                # Détection de fin de partie (Extinction)
                if preys > 0 or preds > 0: life_started = True
                if life_started and preys == 0 and preds == 0:
                    print("\nFin de partie : Population éteinte.")
                    os.kill(env_p.pid, signal.SIGINT)
                    break

            except sysv_ipc.Error:
                break          
    
    except KeyboardInterrupt:
        print("\nArrêt demandé...")
    finally:
        # Nettoyage final : on tue l'environnement qui tuera ses threads
        try: os.kill(env_p.pid, signal.SIGINT)
        except: pass
    
if __name__ == "__main__":
    main()
