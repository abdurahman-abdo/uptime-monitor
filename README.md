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
- **Diagnostics information:** captures the status code, time taken (in milliseconds), URL after the redirects (final URL), number of redirects and the error message for each site.
- **Fault tolerance:** timeouts, unreachable domains, malformed URLs, unsupported schemes (`ftp://`) and error responses are recorded as failed checks and don't stop the run.
- **Report:** summary statistics including total number of checks, number of working/failed sites, % of uptime, average response time and a list of failures.
- **Correct average calculation:** the average is calculated from only successful checks, not counting failures.
- **Input checking:** the absence of a file, incorrect JSON format, incorrect file structure or invalid entries are detected and result in informative messages.
- **Internet-independent testing:** the unit tests operate on fabricated responses and temporary files and work offline.  

## Project structure
uptime-monitor/  
├── project.py # the program: main and three custom functions  
├── test_project.py # pytest tests for those functions 
├── example_sites.json # example list of sites to monitor 
├── requirements.txt # third-party libraries  
└── README.md # this file  

### project.py

- **`main()`** is where the execution starts. It takes the JSON file’s file path as an argument and loads the list of sites. It discards entries without URLs (by printing a warning message), performs a test for every site in the list, and prints the summary. This is the only function that outputs anything on the console screen and also where the exit() function is called. If no file path is specified as an argument, `main()` prints usage and then exits the application. If the number of arguments is wrong (none, or more than one), main() prints a usage message and exits.

- **`check_url(url, timeout, redirects)`** processes a single website and produces a report dictionary which has the same structure with the following keys always: `url`, `final_url`, `status_code`, `response_time_ms`, `is_ok`, `redirects`, and `error`. Any failure it can foresee (connection timeouts, connection errors, invalid URLs, unsupported protocols, error statuses) is captured by a report rather than an exception, so one failed website does not stop other websites from processing.

- **`summarize_results(results)`** processes the list of reports produced by `check_url` and generates a summary report with the following keys: `total_checks`, `number_up`, `number_down`, `uptime`, `average_response_time`, and `failures`. This function performs no network or file I/O, just processes the list.

- **`json_loader(file_name)`** loads the JSON file and returns the list of sites. If the file is missing, is invalid JSON or is of unexpected format, it raises a `ValueError` with an appropriate message. It never prints anything nor quits the program, so it lets `main()` to decide how to display the problem.

### test_project.py

Tests for `check_url`, `summarize_results`, and `json_loader`:

- `check_url` is tested by replacing `requests.get` with a fake response (pytest's `monkeypatch`), so working, not-found and server-error cases can be simulated without any network connection. Malformed and unsupported URLs are tested with the real library, because `requests` rejects them before sending anything.
- `summarize_results` is tested on handcrafted report lists, including both successful and failed ones.
- `json_loader` is tested on small files created in the directory provided by pytest, one for each success and failure case.

### requirements.txt

Provides a list of third-party libraries needed by the project. 

### example_sites.json

A demo input file for trying out the program. It covers a range of outcomes: healthy sites, error pages (404 and 500), a slow response that exceeds its timeout, a redirect chain, a domain that does not exist, an unsupported address (`ftp://`), and one entry with no URL, which the program skips. Results for the `httpbin.org` entries can vary, since it is a public service.

## How it works
1. **Loading the site list.** `main` takes the file path from the command line and passes it to `json_loader`. If the file is missing, is not valid JSON, or has the wrong structure, the loader raises a `ValueError`, and main prints its message and exits before any checks run.

2. **Cleaning the entries.** All entries without `url` field are removed, and a warning is outputted for each skipped entry. In case there are no useful entries left after that, the program stops instead of reporting about zero sites.

3. **Checking each site.** For all other entries, `main` invokes `check_url` function with the site's URL and own values for timeout and redirects options (the default ones are used if options are not provided). `check_url` sends the request and logs:
   - status code,
   - response time in milliseconds,
   - final URL and count of redirects done,
   - check result (`is_ok`),
   - error message, in case of an error

   A status code 4xx or 5xx is considered as an error. Timeout, connection errors, incorrect URLs, and invalid schemes are caught and converted to readable error messages and proceed to the next site.

4. **Summarize the data.** `main()` sends the list of reports to `summarize_results()`. The function tallies the number of sites which were up and down and gets the uptime percentage. It also determines the average response time among those that have succeeded and creates a list of the failed ones with their URL, status code, and error message. The values which could not be determined will be `None`.

5. **Display the results.** `main()` prints the report: the number of sites checked, the uptime percentage, the number up and down, the average response time (or N/A), and the failures with their status codes and reasons, or a message that there were none


## Design decisions
**No response time for failed checks.** In case of total failure (timeout, unreachable domain, wrong URL), the response time will be `None`, not `0`. Otherwise the average will be distorted by an invented value. `None` explicitly denotes the absence of measurement.

**Only successful checks count toward the average response time.** A site that is down shouldn't make the average look faster or slower, but the uptime percentage still counts every check, so failures are never hidden. If no check succeeded, the average is `None`.

**4xx or 5xx response codes are considered downtime.** Server responded, but a user cannot access the page due to an error, therefore it has to be treated as a failure. The statistics list them along with the code. Their response times are not included in average, which is consistent with the above principle.

**`check_url` reports network and HTTP failures instead of raising them, and always returns the same fields.** One bad site therefore can't stop the others from being checked, and code that handles the reports never has to guard against missing keys.

**Redirects are followed by default and can be turned off per site.** A browser follows redirects, so by default the check judges the page a visitor would actually reach, and the report records the final URL and the number of hops. With `"redirects": false`, the first response is the result. A redirect (3xx) is not an error status, so in that mode a site that answers with one counts as up.

**The calculations are separated from input and output.** `summarize_results` contains just arithmetic on the list, `check_url` communicates with websites only, and `json_loader` reads a file. That makes them independent of each other and testable separately. In the future, a web service can use them independently of command line functionality.

**Loader throws exceptions, while `main()` handles them.** `json_loader` throws a `ValueError` with a proper explanation when the file is missing or incorrect. It never prints or exits, which means it may be used in a web service later on. There, an erroneous configuration file should not terminate the entire server process. Only `main()` prints and exits.

**Dropped entries due to lack of URL raise warning.** One invalid line shouldn't affect the checks for the rest of the sites. However, the drawback is that the site may be dropped because of a trivial reason like a typo, therefore a warning is printed for each skipped entry. On failure of checking of all entries program exits without reporting about zero results.

**Any corrupted data leads to a crash.** In case when a successfully checked website doesn't provide any response time, `summarize_results` crashes and doesn't substitute anything implicitly. The problem here is obviously somewhere up the code and such default behavior would hide the problem behind the legitimate average.

**Rounding happens in the very end.** Only in the end of calculations rounding of percentages and averages to two decimals is made to avoid errors caused by using floating-point number.

**The tests pass without any network connection.** All functions requiring network connection return a predefined value instead so tests can easily be done even offline simulating such situations as 500 status or timeout. Cases of errors before any communication are done by the library itself.  

**The source file gets selected via the command line arguments.** The name is an argument rather than a hard-coded one, meaning that a single program can track any set of web addresses, for example, a different file for every customer.

## Configuration file format

The program reads the sites to monitor from a JSON file. The file must contain a **list**, and each item in the list is an object describing one site.

```json
[
  {"url": "https://example.com"},
  {"url": "https://www.github.com", "timeout": 10},
  {"url": "http://github.com", "redirects": false}
]
```
> `example_sites.json` is a demo file, not a template: it contains deliberately broken entries to show how failures are reported. You can start from the small example above for your own list.

### Fields

| Field | Required | Default | Meaning |
|---|---|---|---|
| `url` | yes | none | The full address to check, including `http://` or `https://`. |
| `timeout` | no | 5.0 | Seconds to wait for a response before the check counts as failed. |
| `redirects` | no | true | Whether to follow redirects. If false, the first response is the result, even if it is a redirect. |

Any other fields are ignored.

### What happens with bad input

| Situation | Result |
|---|---|
| The file does not exist | The program stops with an error message that names the file. |
| The file is empty or is not valid JSON | The program stops with an error message. |
| The top level is not a list, or an item is not an object | The program stops with an error message. |
| An entry has no `url` | That entry is skipped, a message is printed for it, and the other sites are still checked. |
| The list is empty (`[]`) | The program stops with an error that the format is invalid. |
| Every entry is skipped | The program stops and reports that there is nothing to check. |

A site that cannot be reached, or an unsupported address such as `ftp://example.com`, is not a configuration error. It is checked like any other site and reported as a failure.

## Installation and usage

### Requirements

- Python (v. 3.10 or newer)
- An internet connection to run the monitor (the tests do not need one)

### Install

1. Get the project:

   ```
   git clone https://github.com/abdurahman-abdo/uptime-monitor.git
   cd uptime-monitor
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   ```

   Windows (PowerShell):
   ```
   venv\Scripts\Activate.ps1
   ```

   macOS / Linux:
   ```
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

### Run

Provide the path to a JSON file with the monitored sites (see [Configuration file format](#configuration-file-format)):

```
python project.py example_sites.json
```

All monitored sites will be checked, and their status will be printed. If the path is missing, the file doesn’t exist, isn’t valid JSON, or doesn’t contain a list of site objects, the program prints an error message and stops.

### Test

```
pytest
```

The tests use fake responses and temporary files, so they run quickly without an internet connection.


## Example output

Running the program on the included demo file:

```
python project.py example_sites.json
```

produces output like this:

```
There was no url key detected for the specific object, thus dropped!
...
================================================
WEBSITE UPTIME MONITOR
================================================

9 websites checked with 44.44% success rate!
------------------------------------------------
Total sites that were up:   4
Total sites that were down: 5
Average response time:      552.06 milliseconds
Failures: [
    {
        "url": "https://httpbin.org/status/404",
        "status_code": 404,
        "error_message": "Resource not found (404)."
    },
    {
        "url": "https://httpbin.org/status/500",
        "status_code": 500,
        "error_message": "Server Error encountered (500)."
    },
    {
        "url": "https://httpbin.org/delay/5",
        "status_code": null,
        "error_message": "The request timed out (more than 2 seconds)."
    },
    {
        "url": "https://this-domain-does-not-exist-12345.com",
        "status_code": null,
        "error_message": "Failed to connect to the server."
    },
    {
        "url": "ftp://example.com",
        "status_code": null,
        "error_message": "An unexpected requests error occurred: No connection adapters were found for 'ftp://example.com'"
    }
]
```

The demo file has ten entries. One has no URL, so it is skipped with a message and not counted, which leaves nine checks. Four were up, giving an uptime of 44.44%, and the average response time of 552.06 ms comes from those four successful checks only. The other five are listed as failures with their status codes and reasons: the 404 and 500 error pages, the endpoint that exceeds its two-second timeout, the domain that does not exist, and the unsupported `ftp://` address. Response times vary from run to run, and the `httpbin.org` entries depend on a public service, so your numbers may differ slightly.

## Testing

The following command will run the tests inside the project folder:

```
pytest
```

Running the tests requires no internet connection and takes just a second. All network requests are substituted with faked ones and file reading is performed with writing small files into the temporary folder and deleting them after pytest has finished.

### What is tested

**`check_url`**
- A dummy response object serves as a stand-in for a website with the help of pytest's `monkeypatch` and allows the tests to check a working (200), not found (404) and a server error (500) response at once, while it is impossible to create such responses against real sites.
- Malformed or unsupported urls (without scheme, `ftp://`, `file://`, `mailto:`) are tested using the real library since the error occurs even without making a network request. Those cases are covered by one parametrized test.

**`summarize_results`**
- Handwritten reports for a mixed result, all websites up, all websites down and an empty list. The expected results were calculated beforehand manually.
- 404 with large response time is included in the list for a mixed result to make sure that there is no failed check in the average value.
- A successful report without a response time raises a `TypeError`.

**`json_loader`**
- A valid file returns exactly the list that was written.
- A missing file, an empty file, text that isn't JSON, an empty list, and valid JSON with the wrong structure (an object, or a list of strings) each raise a `ValueError`, and the tests check the message.

### What is not unit-tested
- **`main()`** reads the command line, makes real requests, prints the report, and exits, so it is verified by running the program on `example_sites.json`.
- **Timeouts, connection errors, and redirect handling in `check_url`** are not covered by unit tests yet. The demo file exercises them against real endpoints instead: a slow response that exceeds its timeout, a domain that does not exist, a redirect chain, and a site with redirects turned off.


## Limitations and future work

### Limitations

- **Only one check per run.** Sites get checked only once, with no data being saved. The uptime percentage reflects the number of successful sites checked in this run, not the uptime in general.
- **One by one sites checking.** The duration of the run depends on the sum of all response times and timeouts, which means the larger the input file and slower sites - the longer it takes.
- **Only time before response is counted.** Response time measures the period of waiting for the response, not the full page loading and rendering.
- **A redirect with redirects turned off counts as up.** With `"redirects": false`, a site that answers with a redirect (3xx) is reported as up, because a redirect is not an error status. The check only shows that the server responded, not that the final page works.
- **Invalid `timeout` values stop the program.** A `timeout` that is not a positive number (for example `"5"`, `0`, or `-1`) makes the `requests` library raise a `ValueError`, which `check_url` does not catch, so the run ends with an error and no report. Other fields are not type-checked either: for instance, the string `"false"` for `redirects` is likely treated as true.
- **Missing entries are not marked.** The program indicates that an entry without a `url` has been skipped, but it doesn’t show which one, and an entry with an empty `url` isn't even skipped; it is processed, and then indicated as failed.
- **Exit code doesn’t indicate sites' availability.** The program fails with an error code only if the input data is incorrect. If sites are unavailable, the program terminates successfully, and therefore scripts cannot handle such situations.
- **Not all errors are caused by the sites.** Some sites don’t allow requests from bots, which makes them appear unavailable, while limited network access may result in timeouts, as evidenced by the GitHub entries in the example.
- **Text output only.** The output is a text report with failed sites presented in JSON format.
- **There are no automated tests for `main()`.** This function is tested manually by using `example_sites.json` file.

### Future works

- **Expiry date of certificates.** Return how many days are left until expiry for the TLS certificate for each of the sites.
- **An exit code that means something.** This would be useful for a scheduler/CI job to know that a site is down.
- **Checks running in parallel.** So a job would take the time of the longest running check and not the sum.
- **History.** Saving the data into a DB for calculating uptime statistics.
- **Web service with a status page.** Using check_url, summarize_results and json_loader, having /health and /status endpoints.
- **Alerts to slack/webhook.** Alerts in case a site goes down or a certificate is about to expire.
- **DevOps tooling.** Docker, Github actions and deployment to some hosting service.