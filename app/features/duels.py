# app/features/duels.py
import socket
import threading
import time
import random
from typing import Dict, Any, Optional, Callable

class NexaDuels:
    CHALLENGES = [
        {
            "type": "code",
            "description": "Write a Python function 'fib(n)' that returns the n-th Fibonacci number.",
            "verify": lambda ans: "def fib" in ans and ("return" in ans or "yield" in ans)
        },
        {
            "type": "design",
            "description": "Describe a clean CSS layout for a dark-mode card component using CSS Grid.",
            "verify": lambda ans: "display: grid" in ans.lower() or "grid-template" in ans.lower()
        },
        {
            "type": "fix",
            "description": "Find the bug in this Python snippet: 'def add(a, b): return a + b' where inputs are strings. Convert them to floats.",
            "verify": lambda ans: "float(" in ans.lower()
        },
        {
            "type": "math",
            "description": "Solve for x: 3x + 12 = 48. What is the value of x?",
            "verify": lambda ans: "12" in ans.strip()
        }
    ]

    def __init__(self, xp_manager=None, ui_callback: Optional[Callable[[str], None]] = None):
        self.xp_manager = xp_manager
        self.ui_callback = ui_callback
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.is_hosting = False
        self.is_joined = False
        self.active_challenge = None
        self.start_time = 0.0

    def get_local_ip(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def generate_code(self) -> str:
        ip = self.get_local_ip()
        last_octet = ip.split(".")[-1]
        port = 7751
        return f"NX-{last_octet}-{port}"

    def host_duel(self) -> str:
        code = self.generate_code()
        ip = self.get_local_ip()
        self.is_hosting = True
        self.active_challenge = random.choice(self.CHALLENGES)
        
        # Start server socket in background
        threading.Thread(target=self._run_server, daemon=True).start()
        return code

    def _run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind(('0.0.0.0', 7751))
            self.server_socket.listen(1)
            if self.ui_callback:
                self.ui_callback(f"[DUEL] Server listening on port 7751. Code generated.")
            
            conn, addr = self.server_socket.accept()
            self.client_socket = conn
            if self.ui_callback:
                self.ui_callback(f"[DUEL] Player joined from {addr[0]}! Duel starting...")

            # Sync challenge and start game
            challenge_desc = self.active_challenge["description"]
            conn.sendall(f"START:{challenge_desc}".encode('utf-8'))
            
            self.start_time = time.time()
            if self.ui_callback:
                self.ui_callback(f"\n⚡ DUEL READY!\nChallenge: {challenge_desc}\n3... 2... 1... GO!")
            
            # Listen for submissions from client
            while self.is_hosting:
                data = conn.recv(1024)
                if not data:
                    break
                msg = data.decode('utf-8')
                if msg.startswith("SUBMIT:"):
                    ans = msg[7:]
                    elapsed = time.time() - self.start_time
                    if self.active_challenge["verify"](ans):
                        conn.sendall(b"LOST")
                        if self.ui_callback:
                            self.ui_callback(f"\n🏆 Opponent wins! Correctly solved in {elapsed:.1f}s.")
                        break
                    else:
                        conn.sendall(b"WRONG")
                        if self.ui_callback:
                            self.ui_callback(f"[DUEL] Opponent submitted incorrect solution.")

        except Exception as e:
            if self.ui_callback:
                self.ui_callback(f"[DUEL] Server error: {str(e)}")
        finally:
            self.close()

    def join_duel(self, code: str) -> str:
        parts = code.strip().split("-")
        if len(parts) != 3 or parts[0] != "NX":
            return "Invalid duel code format. Use NX-[last_octet]-[port]"
        
        last_octet = parts[1]
        port = int(parts[2])
        
        # Reconstruct host IP
        local_ip = self.get_local_ip()
        ip_parts = local_ip.split(".")
        ip_parts[-1] = last_octet
        host_ip = ".".join(ip_parts)
        
        self.is_joined = True
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host_ip, port))
            
            # Start receiver thread
            threading.Thread(target=self._run_client_listener, daemon=True).start()
            return f"Connected to duel lobby at {host_ip}:{port}!"
        except Exception as e:
            self.is_joined = False
            return f"Failed to connect to duel: {str(e)}"

    def _run_client_listener(self):
        try:
            while self.is_joined:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                msg = data.decode('utf-8')
                if msg.startswith("START:"):
                    challenge_desc = msg[6:]
                    self.start_time = time.time()
                    if self.ui_callback:
                        self.ui_callback(f"\n⚡ DUEL READY!\nChallenge: {challenge_desc}\n3... 2... 1... GO!")
                elif msg == "LOST":
                    if self.ui_callback:
                        self.ui_callback("\n🏆 You lost! Opponent solved it first.")
                    break
                elif msg == "WON":
                    if self.ui_callback:
                        elapsed = time.time() - self.start_time
                        self.ui_callback(f"\n🏆 You won! Correctly solved in {elapsed:.1f}s. +200 XP!")
                        if self.xp_manager:
                            self.xp_manager.add_xp("challenge_completed")
                    break
                elif msg == "WRONG":
                    if self.ui_callback:
                        self.ui_callback("Not quite — keep trying. Opponent is still going...")
        except Exception as e:
            if self.ui_callback:
                self.ui_callback(f"[DUEL] Connection error: {str(e)}")
        finally:
            self.close()

    def submit_solution(self, ans: str) -> str:
        if not self.start_time:
            return "No duel is active."
        
        elapsed = time.time() - self.start_time
        if self.is_hosting:
            if self.active_challenge["verify"](ans):
                if self.client_socket:
                    self.client_socket.sendall(b"LOST")
                if self.ui_callback:
                    self.ui_callback(f"\n🏆 You win! Correctly solved in {elapsed:.1f}s. +200 XP!")
                if self.xp_manager:
                    self.xp_manager.add_xp("challenge_completed")
                self.close()
                return "Correct! You won the duel."
            else:
                return "Incorrect solution. Keep trying!"
        elif self.is_joined:
            if self.client_socket:
                self.client_socket.sendall(f"SUBMIT:{ans}".encode('utf-8'))
                return "Solution submitted. Waiting for verification..."
            return "Not connected."
        else:
            # Solo practice
            if self.active_challenge and self.active_challenge["verify"](ans):
                self.close()
                return f"Practice Duel solved in {elapsed:.1f}s! Good job."
            return "Incorrect solution. Keep trying!"

    def practice_solo(self) -> str:
        self.active_challenge = random.choice(self.CHALLENGES)
        self.start_time = time.time()
        return f"\n⚡ PRACTICE DUEL START!\nChallenge: {self.active_challenge['description']}\nGO!"

    def close(self):
        self.is_hosting = False
        self.is_joined = False
        self.start_time = 0.0
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception:
                pass
            self.client_socket = None
