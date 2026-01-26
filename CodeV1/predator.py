import socket
import time
import sys
import subprocess
from multiprocessing import Process

class Predator(Process):
    def __init__(self):
        super().__init__()
        self.energy = 80

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", 6666))
            
            # Inscription
            sock.sendall(b"PREDATOR_JOIN")
            # Recevoir ID (non utilisé mais nécessaire pour le protocole)
            _ = sock.recv(4)

            while self.energy > 0:
                time.sleep(1.5) # Ralentir un peu le cycle de vie
                self.energy -= 2
                
                # Chasse
                if self.energy < 70:
                    sock.sendall(b"GET_PREY")
                    answer = sock.recv(1024).decode()
                    if answer == "HUNTED":
                        # Miam
                        self.energy += 40
                        if self.energy > 100: self.energy = 100
                
                # Reproduction
                if self.energy > 95:
                    self.energy -= 50
                    # On utilise sys.executable pour être robuste
                    subprocess.Popen([sys.executable, "predator.py"])

            # Mort
            sock.sendall(b"PRED_DIE")
            sock.close()
        except Exception:
            pass

if __name__ == "__main__":
    Predator().run()
