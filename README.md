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
## How it works
## Design decisions
## Configuration file format
## Installation and usage
## Example output
## Testing
## Limitations and future work