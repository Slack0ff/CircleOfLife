import time, socket, sys, subprocess, os
from multiprocessing.managers import BaseManager

HOST, MGR_PORT, SOCK_PORT, AUTH_KEY = '127.0.0.1', 50000, 6666, b'circleoflife'

class PreyProcess:
    def __init__(self):
        self.energy = 60
        self.active = False
        
        # Connexion à la mémoire partagée (nécessaire pour manger l'herbe)
        BaseManager.register('get_state')
        self.mgr = BaseManager(address=(HOST, MGR_PORT), authkey=AUTH_KEY)
        self.mgr.connect()
        self.state = self.mgr.get_state()
        
        # Connexion au Socket (pour signaler son état Active/Passive et recevoir la mort)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, SOCK_PORT))
        self.sock.sendall(b"JOIN PREY")
        self.sock.recv(4)
        
        # Socket non-bloquant : essentiel pour vérifier "DEAD" sans bloquer la simulation
        self.sock.setblocking(False)

    def run(self):
        try:
            while self.energy > 0:
                time.sleep(0.5)
                self.energy -= 0.5 
                
                # On regarde si l'Environnement nous a envoyé le signal de mort (mangé)
                try:
                    if self.sock.recv(1024) == b"DEAD": 
                        os.kill(os.getpid(), 9) # Arrêt immédiat
                except: pass

                # Passage en mode ACTIF (Recherche de nourriture, exposée aux prédateurs)
                if self.energy < 60 and not self.active:
                    self.active = True
                    try: self.sock.sendall(b"STATE ACTIVE")
                    except: pass
                    
                # Passage en mode PASSIF (Cachette, sécurité)
                elif self.energy > 85 and self.active:
                    self.active = False
                    try: self.sock.sendall(b"STATE PASSIVE")
                    except: pass

                # On ne peut manger que si on est Actif et qu'il y a de l'herbe
                if self.active and self.state.eat_grass():
                    self.energy += 15
                
                # --- ACTION : REPRODUCTION ---
                if self.energy > 95: 
                    self.energy -= 50
                    subprocess.Popen([sys.executable, "prey.py"])
            
            # Si boucle terminée sans être mangé : Mort par famine
            self.sock.sendall(b"DIE")
            os.kill(os.getpid(), 9)
            
        except KeyboardInterrupt:
            try: self.sock.sendall(b"DIE")
            except: pass
            os.kill(os.getpid(), 9)

if __name__ == "__main__":
    PreyProcess().run()
