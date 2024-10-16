import requests
import socket

def get_http_code(domain, port):
    if not domain or len(domain) > 253:
        return "0"

    try:
        url = f"http://{domain}" if port == 80 else f"https://{domain}"
        response = requests.get(url, timeout=4)
        return str(response.status_code)
    except (requests.RequestException, UnicodeError) as e:
        print(f"Erreur lors de la requête HTTP pour {domain} sur le port {port}: {str(e)}")
        return "0"

def get_ip_address(subdomain):
    if not subdomain or len(subdomain) > 253:
        return "0"

    try:
        ip_address = socket.gethostbyname(subdomain)
        return ip_address
    except (socket.gaierror, UnicodeError):
        return "0"

def get_http_ports_and_ip(subdomain):
    http_code_80 = get_http_code(subdomain, 80)
    http_code_443 = get_http_code(subdomain, 443)
    ip_address = get_ip_address(subdomain)

    if http_code_80 == "0" and http_code_443 == "0":
        return subdomain, "0", "0", ip_address
    else:
        ports = []
        codes = []
        if http_code_80 != "0":
            ports.append("80")
            codes.append(http_code_80)
        if http_code_443 != "0":
            ports.append("443")
            codes.append(http_code_443)
        return subdomain, "-".join(codes), "-".join(ports), ip_address
