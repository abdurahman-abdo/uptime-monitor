import requests
import time

def check_url(url: str, timeout: float = 5.0) -> dict:
    report = {
        "url": url,
        "status_code": None,
        "response_time_ms": None,
        "is_ok": False,
        "error": None
    }
    
    response = requests.get(url, timeout=timeout)
    
    report["status_code"] = response.status_code
    
    return report

def days_until_cert_expiry(hostname: str, port: int = 443) -> int | None:
    """Return days until the TLS cert expires (None for non-HTTPS or failure)."""

def summarize_results(results: list[dict]) -> dict:
    """Return uptime %, average response time, and the list of failing URLs."""

def main():
    """Load targets, run checks, print/store a summary (CLI entry point)."""
    print(check_url(url="https://httpbin.org"))

if __name__ == "__main__":
    main()