import subprocess
import json
import requests
import sys
import time

def get_terraform_outputs():
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd="../infrastructure",
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running terraform: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: terraform not found. Please install terraform.")
        sys.exit(1)

def get_my_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except Exception as e:
        print(f"Could not determine local IP: {e}")
        return "unknown"

def verify_proxy(endpoint, local_ip):
    print(f"\nTesting Proxy: {endpoint}")
    
    # Parse IP from endpoint for display
    try:
        proxy_ip = endpoint.split("@")[1].split(":")[0]
    except:
        proxy_ip = "unknown"

    proxies = {
        "http": endpoint,
        "https": endpoint,
    }

    # 1. Connectivity & IP Check
    start_time = time.time()
    try:
        response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
        latency = (time.time() - start_time) * 1000
        
        try:
            remote_ip = response.json()["origin"]
        except:
            remote_ip = response.text

        print(f"  [✓] Connectivity (Latency: {latency:.2f}ms)")
        
        if local_ip in remote_ip:
            print(f"  [!] FAIL: Real IP leaked! Remote saw: {remote_ip}")
        elif proxy_ip not in remote_ip and proxy_ip != "unknown":
             # Sometimes httpbin shows multiple IPs if chained, but usually should match proxy_ip
             print(f"  [?] WARN: Remote IP ({remote_ip}) does not match Proxy IP ({proxy_ip})")
        else:
            print(f"  [✓] IP Masking Verified (Remote saw: {remote_ip})")

    except Exception as e:
        print(f"  [X] Connection Failed: {e}")
        return

    # 2. Anonymity Check (Headers)
    try:
        response = requests.get("http://httpbin.org/headers", proxies=proxies, timeout=10)
        headers = response.json().get("headers", {})
        
        leaky_headers = ["Via", "X-Forwarded-For", "Forwarded"]
        found_leaks = [h for h in leaky_headers if h in headers]
        
        if found_leaks:
            print(f"  [!] FAIL: Anonymity leaked headers: {found_leaks}")
        else:
            print(f"  [✓] Anonymity Verified (No leaky headers found)")
            
    except Exception as e:
        print(f"  [X] Header Check Failed: {e}")

def main():
    print("=== Proxy Network Verification ===")
    
    print("1. Getting Local IP...")
    local_ip = get_my_ip()
    print(f"   Local IP: {local_ip}")

    print("\n2. Reading Terraform State...")
    outputs = get_terraform_outputs()
    endpoints = outputs.get("proxy_endpoints", {}).get("value", [])
    
    if not endpoints:
        print("   No proxies found in Terraform output.")
        sys.exit(0)
        
    print(f"   Found {len(endpoints)} proxies.")

    print("\n3. Verifying Proxies...")
    for endpoint in endpoints:
        verify_proxy(endpoint, local_ip)

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    main()
