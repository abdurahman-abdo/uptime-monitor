import requests

def check_url(url: str, timeout: float = 5.0, redirects: bool = True) -> dict:
    """This function takes a url, [timeout and redirects, optional], checks whether the url responds as intended, and returns a dictionary containing the status info.

    Args:
        url (str): the url you want to check
        timeout (float, optional): sets a maximum wait time (in seconds) for the server to send any data back. Defaults to 5.0.
        redirects (bool, optional): sets whether the request should follow redirects or just stop when it faces one. Defaults to True.

    Returns:
        dict: with a constant keys of url, the final url, status_code, response_time in microseconds, whether successful or not, amount of redirects, and any errors.
    """
    
    report = {
        "url": url,
        "final_url": url,
        "status_code": None,
        "response_time_ms": None,
        "is_ok": False,
        "redirects": None,
        "error": None
    }
    
    try:
        response = requests.get(url=url, timeout=timeout, allow_redirects=redirects)
        
        report["status_code"] = response.status_code
        report["response_time_ms"] = round(response.elapsed.total_seconds() * 1000, 2)
        report["final_url"] = response.url
        report["redirects"] = len(response.history) if response.history else 0
        
        response.raise_for_status()
        
    except requests.exceptions.Timeout:
        report["error"] = f"The request timed out (more than {timeout} seconds)."
    except requests.exceptions.SSLError:
        report["error"] = "SSL/TLS Certificate Error"
    except requests.exceptions.ConnectionError:
        report["error"] = "Failed to connect to the server."
    except requests.exceptions.InvalidURL:
        report["error"] = "The url was invalid."
    except requests.exceptions.MissingSchema:
        report["error"]= "Error: The URL is missing a scheme (e.g., http:// or https://)."
    except requests.exceptions.HTTPError as err:
        if err.response is not None:
            code = err.response.status_code
            
            if code == 404:
                report["error"] = "Resource not found (404)."
            elif 400 <= code < 500:
                report["error"] = f"Client Error encountered ({code})."
            elif code >= 500:
                report["error"] = f"Server Error encountered ({code})."
            else:
                report["error"] = f"HTTP Error encountered ({code})."
        else:
            report["error"] = f"HTTP Error occurred: {err}"
    except requests.exceptions.RequestException as err:
        report["error"] = f"An unexpected requests error occurred: {err}"
    else:
        report["is_ok"] = True
    
    return report

def days_until_cert_expiry(hostname: str, port: int = 443) -> int | None:
    """Return days until the TLS cert expires (None for non-HTTPS or failure)."""

def summarize_results(results: list[dict]) -> dict:
    """Return uptime %, average response time, and the list of failing URLs."""

def main():
    """Load targets, run checks, print/store a summary (CLI entry point)."""
    print(check_url(url="ftp://example.com", timeout=2))

if __name__ == "__main__":
    main()