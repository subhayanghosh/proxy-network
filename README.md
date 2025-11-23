# Self-Hosted Proxy Network

A scalable, self-hosted proxy network using DigitalOcean Droplets and Squid Proxy. This project allows you to spin up a cluster of proxies with a single command, managed via Terraform.

## Features
- **Automated Deployment**: Provision proxy nodes in minutes using Terraform.
- **Authentication**: Secure username/password authentication.
- **Proxy Manager**: A Python service to track active proxies and serve working IPs.
- **Verification Suite**: Tools to verify anonymity, latency, and connectivity.

## Prerequisites
- **Terraform**: [Install Guide](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- **DigitalOcean Account**: You need an API Token.
- **Python 3**: For the manager and verification scripts.

## Quick Start

### 1. Setup Configuration
Copy the example variables file and add your credentials:
```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
```
Edit `terraform.tfvars`:
```hcl
do_token       = "your_digitalocean_token"
node_count     = 2
region         = "nyc1"
proxy_username = "myuser"
proxy_password = "secure_password_no_percent_signs"
```

### 2. Deploy Network
Initialize and apply the Terraform configuration:
```bash
terraform init
terraform apply
```
Type `yes` to confirm.

### 3. Verify
Check if your proxies are working correctly:
```bash
cd ../verification
pip install -r requirements.txt
python3 verify_network.py
```

## Usage

### Manual
Terraform outputs the proxy endpoints after deployment:
```bash
terraform output proxy_endpoints
```
Use with curl:
```bash
curl -x http://user:pass@ip:3128 http://ifconfig.me
```

### via Proxy Manager
Run the local manager service to get random rotating proxies:
```bash
cd ../proxy-manager
./run.sh
```
Get a proxy:
```bash
curl http://localhost:8000/proxy/random
```

## Project Structure
- `infrastructure/`: Terraform code to provision servers.
- `proxy-manager/`: Python FastAPI service to manage and check proxies.
- `verification/`: Scripts to test proxy health and anonymity.
