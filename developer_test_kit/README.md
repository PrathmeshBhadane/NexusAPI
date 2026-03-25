# API Key Developer Test Kit

This folder contains a simple Python script designed for your developers to independently verify their generated API keys against your running Platform Gateway.

## How to use

First, install the required packages:

```bash
pip install -r requirements.txt
```

Run the Python script by passing the API key you generated from the Developer Dashboard:

```bash
python test_api.py YOUR_API_KEY_HERE
```

## Expected Output

The script tests the key against all local service micro-routers (`/ml`, `/ai`, `/data`, `/auth`). It validates two things:
1. Is the key actually valid? (If no, it returns `401 Unauthorized`).
2. If valid, is the key permitted to access this specific microservice scope? (If restricted, it returns `403 Forbidden`).

This allows developers to verify that their "ML Only" scoped keys actually block access to AI generation routines while verifying that they function normally for model training!
