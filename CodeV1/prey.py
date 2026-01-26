import socket
import time
import sys
import subprocess
from multiprocessing import Process

class Prey(Process):
    def __init__(self):
        super().__init__()
        self.energy = 80
        self.active = False # Active = a faim et cherche à manger

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", 6666))
            
            # Rejoindre
            sock.sendall(b"PREY_JOIN")
            _ = sock.recv(4)
            
            while self.energy > 0:
                time.sleep(1)
                self.energy -= 2
                
                # Gestion de la faim (Active)
                if self.energy < 60 and not self.active:
                    self.active = True
                    sock.sendall(b"SET_ACTIVE")
                
                if self.active:
                    sock.sendall(b"EAT_GRASS")
                    answer = sock.recv(1024).decode()
                    if answer == "OK":
                        self.energy += 30
                        if self.energy > 100:
                            self.energy = 100
                            self.active = False
                            sock.sendall(b"SET_PASSIVE")

                # Reproduction
                if self.energy > 90:
                    self.energy -= 40
                    # On lance une nouvelle proie indépendante
                    subprocess.Popen([sys.executable, "prey.py"])

            # Mort naturelle (famine)
            if self.active:
                sock.sendall(b"SET_PASSIVE")
            
            sock.sendall(b"PREY_DIE")
            sock.close()
        except Exception:
            pass

if __name__ == "__main__":
    Prey().run()
