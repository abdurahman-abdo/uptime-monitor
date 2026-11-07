import requests, json, sys

def main():
    if len(sys.argv) !=2:
        sys.exit("This program requires an argument, i.e, <python_filename> <json_filename>")
    
    try:
        urls = json_loader(sys.argv[1])
    except ValueError as e:
        sys.exit(e)
    
    responses = []
    
    cleaned_urls = []
    for idx, url in enumerate(urls):
        if url.get("url", None) is None:
            print("There was no url key detected, thus dropped!")
            print("...")
            continue
        cleaned_urls.append(urls[idx])
    
    if not cleaned_urls:
        sys.exit("A total of 0 websites checked due to empty or invalid input!!! Exiting...")

    
    for url in cleaned_urls:
        responses.append(check_url(url=url["url"], timeout=url.get("timeout", 5.0,), redirects=url.get("redirects", True)))

    results = summarize_results(responses)
    total_checks = results["total_checks"]
    percentage = results["uptime"]
    up_no = results["number_up"]
    down_no = results["number_down"]
    response_av = results["average_response_time"]
    failures = results["failures"]
    failure_urls = [failure["url"] for failure in failures]
    
    print("================================================")
    print("WEBSITE UPTIME MONITOR")
    print("================================================")
    print(f"\n{total_checks} websites checked with {percentage:.2f}% success rate!")
    print("------------------------------------------------")
    print(f"Total sites that were up:   {up_no}")
    print(f"Total sites that were down: {down_no}")
    print(f"Average response time:      {response_av} milliseconds" if response_av is not None else "Average response time:      N/A")
    # print(f"Failures: {json.dumps(failures, indent=4)}")
    print(f"Failures: {json.dumps(failure_urls, indent=4)}" if failures else "No failures found.")
    print()
    
    # print(json.dumps(results, indent=4))

def check_url(url: str, timeout: float = 5.0, redirects: bool = True) -> dict:
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

def summarize_results(results: list[dict]) -> dict:
    
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

if __name__ == "__main__":
    main()