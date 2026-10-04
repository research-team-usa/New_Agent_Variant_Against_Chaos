# /opt/prime_core_system/prime_core_system.py

import sys
import json
import urllib.request
import urllib.error
import time
import traceback
import hashlib
import sqlite3
import re
import threading
import random
import logging
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# --- KONFIGURATION & LOGGING ---
BACKEND_MODEL = "mistral"
API_PORT = 9090
OLLAMA_URL = "http://localhost:11434/api/chat"
API_KEY = "sk-prime-core-v1"
RATE_LIMIT_REQUESTS = 50
RATE_LIMIT_WINDOW = 60
DB_PATH = "prime_core.db"
LOG_PATH = "prime_core.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- RATE LIMITER & AUTH ---
rate_lock = threading.Lock()
ip_requests = {}

def check_rate_limit(ip_address: str) -> bool:
    current_time = time.time()
    with rate_lock:
        if ip_address not in ip_requests:
            ip_requests[ip_address] = []
        ip_requests[ip_address] = [t for t in ip_requests[ip_address] if current_time - t < RATE_LIMIT_WINDOW]
        if len(ip_requests[ip_address]) >= RATE_LIMIT_REQUESTS:
            logging.warning(f"Rate limit exceeded for IP: {ip_address}")
            return False
        ip_requests[ip_address].append(current_time)
        return True

# --- MATHEMATISCHE BASIS (MILLER-RABIN & HOHE ENTROPIE) ---
def is_probable_prime(n: int, k: int = 10) -> bool:
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
        
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime_signature(text: str) -> int:
    hash_hex = hashlib.sha256(text.lower().strip().encode('utf-8')).hexdigest()
    base_num = int(hash_hex[:12], 16)
    if base_num % 2 == 0:
        base_num += 1
    while not is_probable_prime(base_num):
        base_num += 2
    return base_num

# --- DATENBANK (THREAD-SAFE PER REQUEST) ---
class PrimeDatabase:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path, timeout=15.0)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.cursor = self.conn.cursor()
        self._build_schema()

    def _build_schema(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS registry (prime_sig TEXT PRIMARY KEY, concept TEXT UNIQUE)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS domain_chains (domain TEXT, prime_sig TEXT, UNIQUE(domain, prime_sig))')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain ON domain_chains(domain)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS causal_links (cause_sig TEXT, effect_sig TEXT, UNIQUE(cause_sig, effect_sig))')
        self.conn.commit()

    def store_concept(self, concept: str) -> int:
        prime_sig = generate_prime_signature(concept)
        self.cursor.execute('INSERT OR IGNORE INTO registry (prime_sig, concept) VALUES (?, ?)', (str(prime_sig), concept))
        self.conn.commit()
        return prime_sig

    def link_to_domain(self, domain: str, prime_sig: int):
        self.cursor.execute('INSERT OR IGNORE INTO domain_chains (domain, prime_sig) VALUES (?, ?)', (domain, str(prime_sig)))
        self.conn.commit()

    def get_domain_chain_product(self, domains: list) -> int:
        product = 1
        for domain in domains:
            self.cursor.execute('SELECT prime_sig FROM domain_chains WHERE domain = ?', (domain,))
            for row in self.cursor.fetchall():
                product *= int(row[0])
        return product

    def close(self):
        self.conn.close()

# --- INPUT-KONTROLLE (GLOBAL KNOWLEDGE PROPAGATION) ---
class AxiomExtractor:
    def __init__(self, db: PrimeDatabase):
        self.db = db
        self.stopwords = {"ist", "ein", "und", "oder", "die", "der", "das", "es", "sind", "werden", "durch"}

    def extract_and_store(self, raw_text: str, session_id: str, user_id: str):
        words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]+\b', raw_text.lower())
        for word in words:
            if word not in self.stopwords and len(word) > 2:
                p_sig = self.db.store_concept(word)
                self.db.link_to_domain(session_id, p_sig)
                self.db.link_to_domain(user_id, p_sig)
                self.db.link_to_domain("global", p_sig)

# --- REASONING ENGINE ---
class PrimeReasoningEngine:
    def __init__(self, db: PrimeDatabase):
        self.db = db

    def deduce_path(self, start_concept: str, target_concept: str) -> list:
        start_prime = generate_prime_signature(start_concept)
        target_prime = generate_prime_signature(target_concept)
        queue = deque([[start_prime]])
        visited = {start_prime}

        while queue:
            path = queue.popleft()
            current_prime = path[-1]
            if current_prime == target_prime:
                word_path = []
                for p in path:
                    self.db.cursor.execute('SELECT concept FROM registry WHERE prime_sig = ?', (str(p),))
                    res = self.db.cursor.fetchone()
                    if res: word_path.append(res[0])
                return word_path
            self.db.cursor.execute('SELECT effect_sig FROM causal_links WHERE cause_sig = ?', (str(current_prime),))
            for (effect_sig_str,) in self.db.cursor.fetchall():
                next_prime = int(effect_sig_str)
                if next_prime not in visited:
                    visited.add(next_prime)
                    queue.append(path + [next_prime])
        return []

# --- OUTPUT-KONTROLLE (HIERARCHISCHER VALIDATOR & TOKEN REKONSTRUKTION) ---
class PrimeLLMValidator:
    def __init__(self, db: PrimeDatabase):
        self.db = db
        self.stopwords = {"ist", "ein", "und", "oder", "die", "der", "das", "es", "sind", "werden"}

    def validate_llm_stream(self, llm_output_text: str, active_domains: list) -> str:
        chain_product = self.db.get_domain_chain_product(active_domains)
        if chain_product == 1: 
            return llm_output_text
            
        tokens = re.findall(r'\b\w+\b|\S', llm_output_text)
        validated_output = []
        
        for token in tokens:
            if re.match(r'^[a-zA-ZäöüÄÖÜß]+$', token) and len(token) > 2 and token.lower() not in self.stopwords:
                p_sig = generate_prime_signature(token)
                if chain_product % p_sig == 0:
                    validated_output.append(token)
                else:
                    validated_output.append("[Zensiert: Logikfehler]")
                    logging.warning(f"Halluzination blockiert: {token}")
            else:
                validated_output.append(token)
                
        result = ""
        for token in validated_output:
            if re.match(r'^[.,!?;:]$', token): 
                result += token
            else: 
                result += " " + token if result else token
        return result.strip()

# --- GPU BACKEND (RETRY & TIMEOUT) ---
def fetch_gpu_inference(payload: dict, retries: int = 3) -> str:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30.0) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("message", {}).get("content", "")
        except urllib.error.URLError as e:
            logging.error(f"GPU Inferenz fehlgeschlagen (Versuch {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                return f"[FEHLER]: GPU Backend Timeout/Nicht erreichbar nach {retries} Versuchen: {e}"
        except Exception as e:
            logging.error(f"Unerwarteter Hardware-Fehler: {e}")
            return f"[FEHLER]: Unerwarteter Hardware-Fehler: {e}"

# --- THREADED API SERVER ---
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class PrimeCoreAPI(BaseHTTPRequestHandler):
    def log_message(self, format, *args): 
        pass

    def check_auth(self) -> bool:
        auth_header = self.headers.get('Authorization')
        if not auth_header or auth_header != f"Bearer {API_KEY}":
            self.send_error(401, "Unauthorized")
            logging.warning(f"Unautorisierter Zugriff von {self.client_address[0]}")
            return False
        return True

    def check_rate(self) -> bool:
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip):
            self.send_error(429, "Too Many Requests")
            return False
        return True

    def do_GET(self):
        if self.path == '/v1/models':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"object": "list", "data": [{"id": "Prime-Core-Engine", "object": "model", "created": int(time.time()), "owned_by": "open-origin"}]}
            try: self.wfile.write(json.dumps(response).encode('utf-8'))
            except BrokenPipeError: pass
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self.check_rate() or not self.check_auth():
            return

        # --- NEUE ROUTE: CPU-REASONING / GRAPH-PROOF ---
        if self.path == '/v1/graph/proof':
            db = PrimeDatabase()
            reasoning = PrimeReasoningEngine(db)

            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                req_json = json.loads(post_data.decode('utf-8'))

                start = req_json.get("start", "").strip()
                target = req_json.get("target", "").strip()

                if not start or not target:
                    self.send_error(400, "start/target missing")
                    return

                path = reasoning.deduce_path(start, target)

                if path:
                    result = {
                        "object": "graph.proof",
                        "start": start,
                        "target": target,
                        "path": path,
                        "valid": True
                    }
                else:
                    result = {
                        "object": "graph.proof",
                        "start": start,
                        "target": target,
                        "path": [],
                        "valid": False
                    }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            self.send_error(500, "Internal Server Error")
        finally:
            db.close()
        return

        # --- ALTER GPU-PFAD ---
        if self.path == '/v1/chat/completions':
            db = PrimeDatabase()
            extractor = AxiomExtractor(db)
            validator = PrimeLLMValidator(db)
            ...
            return

        # --- FALLBACK ---
        else:
            self.send_error(404)

def main():
    server_address = ('0.0.0.0', API_PORT)
    httpd = ThreadedHTTPServer(server_address, PrimeCoreAPI)
    logging.info(f"=== PRIME-CORE RUNNING ON PORT {API_PORT} ===")
    httpd.serve_forever()

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt: 
        logging.info("System manuell gestoppt.")
        sys.exit(0)