import subprocess
import json
import random
import time
import threading
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Proxy Manager")

class ProxyNode(BaseModel):
    endpoint: str
    ip: str
    last_checked: float = 0
    is_active: bool = False
    latency_ms: float = 0

class ProxyManager:
    def __init__(self):
        self.proxies: List[ProxyNode] = []
        self.lock = threading.Lock()
        self.running = True
        
        # Start background refresher
        self.refresher_thread = threading.Thread(target=self._background_refresh, daemon=True)
        self.refresher_thread.start()

    def load_proxies_from_terraform(self):
        """Reads terraform output to find proxies."""
        try:
            # Run terraform output -json in the infrastructure directory
            result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd="../infrastructure",
                capture_output=True,
                text=True,
                check=True
            )
            outputs = json.loads(result.stdout)
            
            # Parse the proxy_endpoints output
            # Expected format: ["http://user:pass@ip:3128", ...]
            endpoints = outputs.get("proxy_endpoints", {}).get("value", [])
            
            new_proxies = []
            for endpoint in endpoints:
                # Extract IP for metadata (simple parsing)
                # http://user:pass@1.2.3.4:3128
                try:
                    ip = endpoint.split("@")[1].split(":")[0]
                    new_proxies.append(ProxyNode(endpoint=endpoint, ip=ip))
                except IndexError:
                    print(f"Failed to parse endpoint: {endpoint}")
            
            with self.lock:
                # Merge with existing to keep stats if possible, or just replace for now
                self.proxies = new_proxies
                print(f"Loaded {len(self.proxies)} proxies from Terraform.")
                
        except subprocess.CalledProcessError as e:
            print(f"Error running terraform: {e}")
        except Exception as e:
            print(f"Error loading proxies: {e}")

    def check_proxy(self, proxy: ProxyNode):
        """Checks if a proxy is working."""
        proxies = {
            "http": proxy.endpoint,
            "https": proxy.endpoint,
        }
        try:
            start = time.time()
            # Timeout is short to fail fast
            response = requests.get("http://ifconfig.me", proxies=proxies, timeout=5)
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200:
                proxy.is_active = True
                proxy.latency_ms = latency
            else:
                proxy.is_active = False
        except Exception:
            proxy.is_active = False

    def _background_refresh(self):
        """Periodically reloads and checks proxies."""
        while self.running:
            print("Refreshing proxy list...")
            self.load_proxies_from_terraform()
            
            # Check all proxies
            threads = []
            with self.lock:
                current_proxies = list(self.proxies)
            
            for proxy in current_proxies:
                t = threading.Thread(target=self.check_proxy, args=(proxy,))
                t.start()
                threads.append(t)
            
            for t in threads:
                t.join()
                
            print("Proxy refresh complete.")
            time.sleep(60) # Refresh every minute

    def get_random_proxy(self) -> Optional[ProxyNode]:
        with self.lock:
            active = [p for p in self.proxies if p.is_active]
            if not active:
                # If no active proxies, try any proxy as a fallback
                if self.proxies:
                    return random.choice(self.proxies)
                return None
            return random.choice(active)

    def get_all_proxies(self) -> List[ProxyNode]:
        with self.lock:
            return list(self.proxies)

manager = ProxyManager()

@app.get("/")
def read_root():
    return {"status": "running", "active_proxies": len([p for p in manager.get_all_proxies() if p.is_active])}

@app.get("/proxy/random")
def get_random_proxy():
    proxy = manager.get_random_proxy()
    if not proxy:
        raise HTTPException(status_code=503, detail="No active proxies available")
    return proxy

@app.get("/proxy/all")
def get_all_proxies():
    return manager.get_all_proxies()

@app.post("/proxy/refresh")
def trigger_refresh():
    manager.load_proxies_from_terraform()
    return {"status": "Refresh triggered"}
