# Network Diagnostic Tool

## Overview
The Network Diagnostic Tool is a Python-based command-line program designed to help diagnose common network connectivity issues. The tool performs several network checks including connectivity testing, DNS resolution, gateway detection, and port scanning. It then generates a report and provides a simple diagnosis of the network's condition.

This project demonstrates practical use of network programming, system command execution, socket communication, and regular expression parsing in Python.

---

## Features

### System Information
The program collects basic networking information from the system:

- Hostname detection – identifies the computer/device name
- Local IP detection – determines the device's internal network address
- Default gateway detection – identifies the router used for outbound traffic

---

### Connectivity Testing

The tool performs multiple connectivity tests to determine the health of the network.

**Ping Test**
- Sends a ping request to Google's public DNS server (8.8.8.8)
- Verifies whether basic IP connectivity exists
- Attempts to measure round-trip latency

**Web Connection Test**
- Attempts an HTTP request to https://www.google.com
- Confirms whether web access is functioning

**DNS Lookup Test**
- Resolves google.com into an IP address
- Verifies whether DNS services are working correctly

---

## Network Diagnosis

After all tests are completed, the tool analyzes the results and provides a simple diagnosis of the network state.

Possible outcomes include:

- No connectivity detected
- DNS failure
- Web access failure
- Ping blocked but internet working
- Fully operational network

---

## Report Generation

All collected information is written to a file called:

network_report.txt

The report includes:

- System information
- Connectivity test results
- DNS results
- Port scan results
- Final network diagnosis

---

## Technologies Used

- Python
- socket – network communication
- subprocess – executing system networking commands
- platform – detecting operating system
- re – parsing command output using regular expressions
- urllib – performing HTTP requests

---

## Supported Operating Systems

The program automatically adapts its behavior depending on the OS.

Windows:
- Uses `ipconfig` to detect the default gateway

Linux:
- Uses `ip route`

macOS:
- Uses `netstat -rn`

---

## Installation

Clone the repository:

git clone https://github.com/yourusername/network-diagnostic-tool.git

Navigate into the project directory:

cd network-diagnostic-tool

No external dependencies are required since the program uses Python's standard library.

---


## Example Output

==================================================
Network Diagnostic Tool
==================================================

Hostname: MyComputer  
Local IP Address: 192.168.1.5  
Default Gateway: 192.168.1.1  

--- Connectivity Tests ---  
Ping Test: Ping successful: 24 ms  
Web Test: Web access successful  

--- DNS Test ---  
DNS Resolution Successful: google.com -> 142.250.72.14  

--- Port Scan ---  
Resolved google.com to 142.250.72.14  
Open common ports found: 80, 443  

--- Diagnosis ---  
Network appears fully operational.  

Report saved to network_report.txt

---

## Learning Objectives

This project demonstrates several important networking and programming concepts:

- TCP socket communication
- DNS resolution
- Basic port scanning techniques
- OS-specific networking commands
- Regular expression parsing
- Network troubleshooting logic
- File report generation

