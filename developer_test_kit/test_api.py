import requests
import sys
import argparse
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# Default Gateway URL
DEFAULT_GATEWAY_URL = "http://localhost:8000"

# Service test endpoints
SERVICE_ENDPOINTS = {
    "auth": "/auth/health", 
    "ml": "/ml/health",     
    "ai": "/ai/health",     
    "data": "/data/health"  
}

def test_api_key(api_key: str, gateway_url: str):
    print(f"\n{Style.BRIGHT}🚀 Starting API Key Verification...{Style.RESET_ALL}")
    print(f"Gateway URL: {gateway_url}")
    print(f"API Key:     {api_key[:8]}...[REDACTED]")
    print("-" * 50)

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    results = {}
    
    # Test each service scope
    for service, path in SERVICE_ENDPOINTS.items():
        url = f"{gateway_url}{path}"
        print(f"Testing {service.upper()} service scope ({path})... ", end="")
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}✅ SUCCESS (200 OK){Style.RESET_ALL}")
                results[service] = "Success"
            elif response.status_code == 403:
                print(f"{Fore.YELLOW}⚠️ FORBIDDEN (403) - Key does not have '{service}' scope.{Style.RESET_ALL}")
                results[service] = "Forbidden (Scope Restricted)"
            elif response.status_code == 401:
                print(f"{Fore.RED}❌ UNAUTHORIZED (401) - Invalid Key.{Style.RESET_ALL}")
                results[service] = "Unauthorized"
            elif response.status_code == 404:
                print(f"{Fore.YELLOW}❓ NOT FOUND (404) - Route doesn't exist but key might be valid.{Style.RESET_ALL}")
                results[service] = "Route Not Found"
            else:
                print(f"{Fore.RED}❌ ERROR ({response.status_code}) - {response.text}{Style.RESET_ALL}")
                results[service] = f"Error {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}❌ FAILED - Gateway unreachable.{Style.RESET_ALL}")
            results[service] = "Connection Error"
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}❌ TIMEOUT - Service took too long to respond.{Style.RESET_ALL}")
            results[service] = "Timeout"

    print("\n" + "=" * 50)
    print(f"{Style.BRIGHT}📊 Summary Report:{Style.RESET_ALL}")
    for srv, res in results.items():
        status_color = Fore.GREEN if res == "Success" else Fore.YELLOW if "Scope" in res else Fore.RED
        print(f"- {srv.upper():<5} : {status_color}{res}{Style.RESET_ALL}")

    print("=" * 50)
    if all(res == "Unauthorized" for res in results.values()):
        print(f"\n{Fore.RED}Conclusion: The API key is completely INVALID or REVOKED.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.GREEN}Conclusion: The API Key is ACTIVE.{Style.RESET_ALL}")
        print("Check the Summary Report to see which services this key is authorized to access.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test AI Platform API Keys against the API Gateway.")
    parser.add_argument("api_key", help="The API key to test")
    parser.add_argument("--url", default=DEFAULT_GATEWAY_URL, help="API Gateway base URL (default: http://localhost:8000)")
    
    args = parser.parse_args()
    
    test_api_key(args.api_key, args.url)
