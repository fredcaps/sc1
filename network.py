import requests
import socket

def get_http_code(domain, port):
    if not domain or len(domain) > 253:
        return "N/A"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'
    }

    try:
        url = f"http://{domain}" if port == 80 else f"https://{domain}"
        response = requests.get(url, headers=headers, timeout=4, allow_redirects=True)  # Suivi des redirections
        return response.status_code
    except (requests.RequestException, UnicodeError):
        return "N/A"

def get_ip_address(subdomain):
    if not subdomain or len(subdomain) > 253:
        return "N/A"

    try:
        ip_address = socket.gethostbyname(subdomain)
        return ip_address
    except (socket.gaierror, UnicodeError):
        return "N/A"

def get_http_ports_and_ip(subdomain):
    http_code_80 = get_http_code(subdomain, 80)
    http_code_443 = get_http_code(subdomain, 443)
    ip_address = get_ip_address(subdomain)

    if http_code_80 == "N/A" and http_code_443 == "N/A":
        return subdomain, "N/A", "N/A", ip_address
    else:
        ports = []
        if http_code_80 != "N/A":
            ports.append("80")
        if http_code_443 != "N/A":
            ports.append("443")

        return subdomain, f"{http_code_80}-{http_code_443}", "-".join(ports), ip_address
