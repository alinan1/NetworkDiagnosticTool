import socket              
import subprocess          
import platform           
import re                 
from urllib.request import urlopen  
from urllib.error import URLError    

def get_hostname():
    return socket.gethostname() # Returns the computer/device name


def get_local_ip():
    # This method tries to find the local IP address by creating a dummy socket connection.
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # Creates an IPv4 UDP socket --> use UDP because we won't actually send data, so it's faster and doesn't require a real connection
        s.connect(("8.8.8.8", 80))                             # Pretends to connect to Google's DNS server, which helps determine the local IP --> “If I wanted to send data to 8.8.8.8, which network interface and IP address would I use?”
        ip = s.getsockname()[0]                                # Gets the local IP address that would be used for that connection (the first part of the socket's own address)
        s.close()                                              # Closes the socket after we're done with it
        return ip                                              # Returns the detected local IP
    except Exception:
        return "Unavailable"                                 


def get_default_gateway():
    # This method tries to find the default gateway (router IP) by running system commands and parsing their output.

    system_name = platform.system()  # Detects the OS: Windows, Linux, or Darwin (Mac)

    try:

        # WINDOWS 
        if system_name == "Windows":

            output = subprocess.check_output("ipconfig", shell=True, text=True, errors="ignore")
            # subprocess can run terminal commands and capture their output
            # Runs ipconfig and stores its output as text
            # shell=True allows us to run the command as if we were in a terminal, which is needed for some commands on Windows
            # text=True makes the output a string instead of bytes, which is easier to work with
            # errors="ignore" prevents it from crashing if there are any weird characters in the output

            match = re.search(r"Default Gateway[ .:]*([\d.]+)", output)
            # Looks in the text output for something that matches a default gateway IP
            # [ .:]* matches the spacing/dots between "Default Gateway" and the IP
            # ([\d.]+) matches digits and dots of the IP address (example: 192.168.0.1)

            if match:
                return match.group(1)  # Returns the gateway IP if found #group 1 is the part of the regex in parentheses, which is the actual IP address we want

        # LINUX 
        elif system_name == "Linux":

            output = subprocess.check_output(["ip", "route"], text=True, errors="ignore")
            # On many Linux systems, 'ip route' shows routing info
            # ip route prints the routing table including the default gateway

            match = re.search(r"default via ([\d.]+)", output)
            # Looks for something like: default via 192.168.1.1

            if match:
                return match.group(1)  # Returns the gateway if found

        #  MACOS 
        elif system_name == "Darwin":

            output = subprocess.check_output("netstat -rn", shell=True, text=True, errors="ignore")
            # On macOS, 'netstat -rn' shows the routing table

            for line in output.splitlines():  # Goes through output line by line

                if line.startswith("default"):
                    parts = line.split()     # Splits the line into pieces

                    if len(parts) >= 2:      # If there are at least 2 pieces
                        return parts[1]      # The second piece is usually the gateway IP


        return "Unavailable"   # If no method worked, say unavailable

    except Exception:
        return "Unavailable"   


def ping_host(host="8.8.8.8"):
    # This method tries to ping a host to check if it's reachable. It uses different command options based on the operating system.
    #were pinging 8.8.8 because it's Google's public DNS server, which is almost always up and reachable if you have an internet connection

    system_name = platform.system()  

    if system_name == "Windows":
        command = ["ping", "-n", "1", host]   # Windows uses -n for number of pings
    else:
        command = ["ping", "-c", "1", host]   # Mac/Linux use -c for count

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        # Runs the ping command
        # capture_output=True stores terminal output instead of printing it
        # text=True makes the output a string instead of bytes
        # timeout=5 stops it if it hangs too long 

        output = result.stdout + result.stderr   # Combines normal output and error output # we combine 

        if result.returncode == 0:
            # returncode 0 usually means the command succeeded

            time_match = re.search(r"time[=<]?\s*([\d.]+)\s*ms", output, re.IGNORECASE)
            # Tries to find something like "time=23 ms" in the ping output

            if time_match:
                return True, f"Ping successful: {time_match.group(1)} ms"
                # Returns success plus the ping time if found

            return True, "Ping successful"   # return success without time if we couldn't parse it, but it still worked
        else:
            return False, "Ping failed"      # Nonzero return code means ping did not work

    except subprocess.TimeoutExpired:        #TimeoutExpired is raised if the ping command takes longer than the specified timeout 
        return False, "Ping timed out"       # If ping takes too long
    except Exception as e:
        return False, f"Ping error: {e}"     #other error


def check_web_connection():
   # This method tries to access a website (Google) to check if web access is working. It uses urlopen which is a simple way to make an HTTP request.
    try:
        with urlopen("https://www.google.com", timeout=5) as response:
            # Tries to open Google's website within 5 seconds

            if response.status == 200:
                return True, "Web access successful"   # 200 means the site responded normally

            return False, f"Web access returned status code {response.status}"
            # If a strange status code comes back, report it

    except URLError:
        return False, "Could not reach the web"   # Specific web connection error
    except Exception as e:
        return False, f"Web check error: {e}"     #other error


def dns_lookup(domain="google.com"):
    # This method tries to resolve a domain name into an IP address using socket.gethostbyname, which is a simple way to test if DNS is working.
    try:
        ip = socket.gethostbyname(domain)   # Resolves the domain into an IPv4 address
        return True, ip                     # Success: return True and the IP
    except socket.gaierror:                 # gaierror is raised when the address-related error occurs, such as when the domain cannot be resolved
        return False, "DNS lookup failed"   # Domain could not be resolved
    except Exception as e:
        return False, f"DNS error: {e}"     #other DNS-related error


def scan_common_ports(host, ports=None):
    # This method tries to connect to a list of common ports on the target host to see if they are open. It uses TCP sockets for this.
    if ports is None:
        ports = [20, 21, 22, 23, 25, 53, 80, 110, 123, 143, 443, 445, 3389, 8080]
        # Default list of common ports:
        # 20/21 FTP, 22 SSH, 23 Telnet, 25 SMTP, 53 DNS, 80 HTTP, 110 POP3, 123 NTP, 143 IMAP, 443 HTTPS,445 SMB, 3389 RDP, 8080 alternative web port

    open_ports = []   # Empty list to store the ports that are found open

    for port in ports:   # Goes through each port one by one
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Creates a TCP socket because ports are usually checked with TCP

            sock.settimeout(0.5)   # Only wait half a second per port --> dont want to wait long for each port, especially if many are closed (closed ports often take longer to respond)

            result = sock.connect_ex((host, port))
            # Tries to connect to the host on that port
            # connect_ex returns 0 if successful
            #if not successful, it returns an error code (like 111 for connection refused), but we only care if it's 0 or not

            if result == 0:
                open_ports.append(port)   # If connection worked --> that port is open

            sock.close()   # Close socket after checking each port

        except Exception:
            pass   # Ignore errors and move to next port

    return open_ports   # Return the full list of open ports found


def explain_results(ping, web, dns, local_ip, gateway):
    
    print("\n--- Diagnosis ---")

    # return and print is used so that we can both show the diagnosis in the terminal
    # and also save it into the report file.
    if local_ip == "Unavailable":
        diagnosis = "Could not determine local IP. There may be a local network adapter issue."
        print(diagnosis)
        return diagnosis
        # if computer cant find its own local IP, it suggests a problem with the network adapter or configuration

    if gateway == "Unavailable":
        print("Could not detect default gateway automatically.")
    else:
        print("Default gateway was detected, which suggests the device is connected to a local network.")
        # If gateway exists, the machine is probably connected to a router/local network

    # Check all possible combinations of ping, web, and DNS results
    if not ping and not web and not dns:
        diagnosis = "No connectivity detected."
        # All tests failed likely no internet connection, router issue, or major network configuration problem

    elif ping and not web and not dns:
        diagnosis = "IP connectivity works but web and DNS fail."
        # Can reach an IP, but DNS and web fail

    elif not ping and web and not dns:
        diagnosis = "Web access works but ping and DNS failed."
        # Unusual case

    elif not ping and not web and dns:
        diagnosis = "DNS works but general connectivity failed."
        # DNS reachable but host connectivity failing

    elif ping and web and not dns:
        diagnosis = "Internet works but DNS lookup failed."
        # IP connectivity and web access work but DNS test failed

    elif ping and not web and dns:
        diagnosis = "Ping and DNS work but web access failed."
        # Network connectivity exists but HTTP/HTTPS requests failing

    elif not ping and web and dns:
        diagnosis = "Ping blocked but internet access works."
        # Web and DNS work but ping fails

    elif ping and web and dns:
        diagnosis = "Network appears fully operational."
        # All tests succeeded

    print(diagnosis)
    return diagnosis


def save_report(filename, report_lines):
    # This method writes the collected diagnostic results into a text file.
    try:
        with open(filename, "w") as file:
            file.write("NETWORK DIAGNOSTIC REPORT\n")
            file.write("=" * 50 + "\n")

            for line in report_lines:
                file.write(line + "\n")

        print(f"\nReport saved to {filename}")

    except Exception as e:
        print(f"Error saving report: {e}")


def main():
    print("=" * 50)         # Prints a line of 50 = signs
    print("        Network Diagnostic Tool")
    print("=" * 50)

    report_lines = []       # This list stores all results we want to save into the file

    hostname = get_hostname()         # Gets the computer name
    local_ip = get_local_ip()         # Gets local IP address
    gateway = get_default_gateway()   # Gets default gateway/router IP

    print(f"\nHostname: {hostname}")
    print(f"Local IP Address: {local_ip}")
    print(f"Default Gateway: {gateway}")

    report_lines.append(f"Hostname: {hostname}")
    report_lines.append(f"Local IP Address: {local_ip}")
    report_lines.append(f"Default Gateway: {gateway}")

    print("\n--- Connectivity Tests ---")
    ping_ok, ping_message = ping_host("8.8.8.8")
    # Pings Google's DNS server to test network reachability

    print(f"Ping Test: {ping_message}")
    report_lines.append(f"Ping Test: {ping_message}")

    web_ok, web_message = check_web_connection()
    # Tries reaching a website to test actual web access

    print(f"Web Test: {web_message}")
    report_lines.append(f"Web Test: {web_message}")

    print("\n--- DNS Test ---")
    dns_ok, dns_result = dns_lookup("google.com")
    # Checks whether DNS can resolve google.com into an IP

    if dns_ok:
        print(f"DNS Resolution Successful: google.com -> {dns_result}")
        report_lines.append(f"DNS Resolution Successful: google.com -> {dns_result}")
    else:
        print(f"DNS Test: {dns_result}")
        report_lines.append(f"DNS Test: {dns_result}")

    print("\n--- Port Scan ---")
    target = input("Enter a host to scan common ports on (example: google.com): ").strip()
    # Asks user which host they want to scan

    if target:
        # Only run the scan if the user actually typed something
        try:
            target_ip = socket.gethostbyname(target)
            # Converts the hostname into an IP first

            print(f"Resolved {target} to {target_ip}")
            report_lines.append(f"Target Host: {target}")
            report_lines.append(f"Resolved Target IP: {target_ip}")

            open_ports = scan_common_ports(target_ip)
            # Scans the common ports on that IP

            if open_ports:
                ports_text = ", ".join(str(port) for port in open_ports)
                print("Open common ports found:", ports_text)
                report_lines.append(f"Open Common Ports: {ports_text}")
                # Turns port numbers into strings and joins them with commas
            else:
                print("No common open ports found (or they are filtered).")
                report_lines.append("Open Common Ports: None found (or they are filtered).")

        except Exception as e:
            print(f"Could not scan host: {e}")
            report_lines.append(f"Port Scan Error: {e}")
            # If the hostname is invalid or scan fails

    else:
        print("No host entered. Skipping port scan.")
        report_lines.append("Port Scan: Skipped")
        # If user presses enter without typing anything

    diagnosis_message = explain_results(ping_ok, web_ok, dns_ok, local_ip, gateway)
    # Prints a final diagnosis based on all the earlier test results
    report_lines.append(f"Diagnosis: {diagnosis_message}")

    save_report("network_report.txt", report_lines)
    # Saves all collected results into a text file

    print("\nDone.")


if __name__ == "__main__":
    main()
    # This makes sure main() only runs when this file is executed directly