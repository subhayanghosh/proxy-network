# Verification Suite

This directory contains scripts to verify the health and anonymity of your proxy network.

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Verification

Run the verification script:
```bash
python3 verify_network.py
```

## What it tests

1.  **Connectivity**: Can we connect to the internet via the proxy?
2.  **Latency**: How long does a request take?
3.  **IP Masking**: Does the remote server see the Proxy IP instead of your Real IP?
4.  **Anonymity**: Are headers like `X-Forwarded-For` or `Via` stripped?
