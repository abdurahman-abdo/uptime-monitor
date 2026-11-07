# Uptime Monitor
#### Video Demo: [YouTube URL]
#### Description:
Uptime Monitor is a tool that checks a list of websites you provide to it in a JSON file and gives you a report on their status, average response time, and reasons for failure.  
It performs the check individually for each website using the timeout and redirect configuration set by the user or uses default values if not provided, then it generates an overall uptime rate, an average response time, and a list of failures.  
I built it to serve as a starting point for the development of a client-oriented monitoring service, with separate functions for checking, summarizing, and loading so that each part can scale easily.  

## What it does
The Uptime Monitor uses a JSON configuration file to retrieve a list of websites, perform the checks, and then produce a report containing information about which websites are up, their response time, and which failed.

For every single website, the tool makes a request to it and saves the following information: status code, response time in milliseconds, the URL at which the response was obtained, number of redirects, and possible error message, in case of a failure. Every website may have its own timeout and redirect flag, having reasonable default values when the ones are absent.

After checking all websites from the list, the tool creates a summary report: number of checked websites, number of up and down websites, percentage of websites up, average response time of successful requests, and list of failed websites.

In case the input file is missing or has invalid content, the tool terminates and does not make any checks.

## Features
- **Multi-site checks:** verifies any number of websites specified in a JSON file.
- **Site-specific options:** each site can have a different timeout and a flag indicating whether to follow redirects or not, with default values for unspecified properties.
- **Diagnostics information:** captures the status code, time taken (in milliseconds), URL after the redirections (final URL), number of redirections and the error message for each site.
- **Fault tolerance:** timeout, non-reachable domain, invalid URL or unsupported schemes (`ftp://`) cause failure and do not crash the application.
- **Report:** summary statistics including total number of checks, number of working/failed sites, % of uptime, average response time and a list of failures.
- **Correct average calculation:** the average is calculated from only successful checks, not counting failures.
- **Input checking:** the absence of a file, incorrect JSON format, incorrect file structure or invalid entries are detected and result in informative messages.
- **Internet-independent testing:** the unit tests operate on fabricated responses and temporary files and work offline.  

## Project structure
uptime-monitor/
├── project.py # the program: main and three custom functions
├── test_project.py # pytest tests for those functions
├── requirements.txt # third-party libraries
└── README.md # this file


### project.py

- **`main()`** serves as the entry point function. It loads the site list, removes entries without URLs (logging a message for each such entry), processes each remaining site, generates a report, and prints the report. This is the only place where printing messages and quitting the program happens.

- **`check_url(url, timeout, redirects)`** processes a single website and produces a report dictionary which has the same structure with the following keys always: `url`, `final_url`, `status_code`, `response_time_ms`, `is_ok`, `redirects`, and `error`. Any failure it can foresee (connection timeouts, connection errors, invalid URLs, unsupported protocols, error statuses) is captured by a report rather than an exception, so one failed website does not stop other websites from processing.

- **`summarize_results(results)`** processes the list of reports produced by `check_url` and generates a summary report with the following keys: `total_checks`, `number_up`, `number_down`, `uptime`, `average_response_time`, and `failures`. This function performs no network or file I/O, just processes the list.

- **`json_loader(file_name)`** loads the JSON file and returns the list of sites. If the file is missing, is invalid JSON or is of unexpected format, it raises a `ValueError` with an appropriate message. It never prints anything nor quits the program, so it lets `main()` to decide how to display the problem.

### test_project.py

Tests for `check_url`, `summarize_results`, and `json_loader`:

- `check_url` is tested by mocking the request, using `monkeypatch` provided by pytest, replacing the actual request with a fake response. This means that no network connection is required to run the tests because the error cases for the function are checked before any network operation takes place.
- `summarize_results` is tested on handcrafted report lists, including both successful and failed ones.
- `json_loader` is tested on small files created in the directory provided by pytest, one for each success and failure case.

### requirements.txt

Provides a list of third-party libraries needed by the project. 

## How it works
1. **Loading the site list.** The `main` function invokes `json_loader`, which loads the JSON file. In case of a file absence or invalidity, or if its format is wrong, the loader returns an error and stops `main` with the respective error message before any other work starts.

2. **Cleaning the entries.** All entries without `url` field are removed, and a warning is outputted for each skipped entry. In case there are no useful entries left after that, the program stops instead of reporting about zero sites.

3. **Checking each site.** For all other entries, `main` invokes `check_url` function with the site's URL and own values for timeout and redirects options (the default ones are used if options are not provided). `check_url` sends the request and logs:
   - status code,
   - response time in milliseconds,
   - final URL and count of redirects done,
   - check result (`is_ok`),
   - error message, in case of an error

   A status code 4xx or 5xx is considered as an error. Timeout, connection errors, incorrect URLs, and invalid schemes are caught and converted to readable error messages and proceed to the next site.

4. **Summarize the data.** `main()` sends the list of reports to `summarize_results()`. The function tallies the number of sites which were up and down and gets the uptime percentage. It also determines the average response time among those that have succeeded and creates a list of the failed ones with their URL, status code, and error message. The values which could not be determined will be `None`.

5. **Display the results.** `main()` displays the result in a neat format on the terminal – the number of sites tested, the percentage uptime, the number of sites up and down, the average response time (or `N/A`), and the failed attempts.


## Design decisions
## Configuration file format
## Installation and usage
## Example output
## Testing
## Limitations and future work