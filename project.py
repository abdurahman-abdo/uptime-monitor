import requests, json, sys

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
    """Summarize URL checks into their counts, uptime, and failures.

    Args:
        results (list[dict]): Report dictionaries returned by check_url. The keys
            used are "is_ok", "response_time_ms" (milliseconds), "url",
            "status_code", and "error" (error message).

    Returns:
        A dictionary that always has the same keys:
            total_checks (int): number of reports received.
            number_up (int): reports where "is_ok" is true.
            number_down (int): total_checks minus number_up.
            uptime (float | int | None): percentage of checks that were
                up, rounded to 2 decimals. None if there are no checks.
            average_response_time (float | None): mean response time in
                milliseconds across successful checks only, rounded to
                2 decimals. None if there are no successful checks.
            failures (list[dict]): one entry per failed check, each with
                "url", "status_code", and "error_message". Empty if
                every check succeeded.

    Notes:
        Any check where "is_ok" is false counts as down, including a
        404 or 500, even though the server responded. Down checks are
        excluded from the average response time, and a check that never
        got a response has no time to include anyway.

        Empty list: uptime and average_response_time are both None.
        All checks failed: uptime is 0 and average_response_time is None.
    """
    
    total_checks = len(results)
    number_up = 0
    response_time = 0
    failed_urls_info = []
    
    for site in results:
        if site.get("is_ok"):
            number_up += 1
            response_time += site.get("response_time_ms")
        else:
            failed_urls_info.append({"url": site.get("url"), "status_code": site.get("status_code"), "error_message": site.get("error")})

    if total_checks == 0:
        uptime_percentage = None
        average_response_time = None
    elif number_up == 0:
        uptime_percentage = 0
        average_response_time = None
    else:
        uptime_percentage = round((number_up/total_checks * 100), 2)
        average_response_time = round(response_time/number_up, 2)
        
    result = {
        "total_checks": total_checks,
        "number_up": number_up,
        "number_down": total_checks - number_up,
        "uptime": uptime_percentage,
        "average_response_time": average_response_time,
        "failures": failed_urls_info
    }
    
    return result
    
def json_loader(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            urls = json.load(file)
    except FileNotFoundError:
        raise ValueError(f"The file {file_name} was not found!")
    except json.JSONDecodeError:
        raise ValueError("The JSON file is corrupted or empty!")
    
    if not urls or not isinstance(urls, list) or not all(isinstance(url, dict) for url in urls):
        raise ValueError("The json format was invalid!")
    
    return urls
def main():
    """Load targets, run checks, print/store a summary (CLI entry point)."""
    try:
        urls = json_loader("sample.json")
    except ValueError as e:
        sys.exit(e)
    
    responses = []
    
    cleaned_urls = []
    for idx, url in enumerate(urls):
        if url.get("url", None) is None:
            print("There was no url key detected, thus dropped!")
            continue
        cleaned_urls.append(urls[idx])

    for url in cleaned_urls:
        responses.append(check_url(url=url["url"], timeout=url.get("timeout", 5.0,), redirects=url.get("redirects", True)))

if __name__ == "__main__":
    main()