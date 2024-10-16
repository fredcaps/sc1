import concurrent.futures
from datetime import datetime
from network import get_http_ports_and_ip

def filter_and_write_results(subdomains, domain, output_file):
    unique_subdomains = set(subdomains)

    with open(output_file, 'a') as f:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(get_http_ports_and_ip, subdomain): subdomain for subdomain in unique_subdomains}

            for future in concurrent.futures.as_completed(futures):
                try:
                    subdomain, http_codes, ports, ip_address = future.result()
                    if "0" not in http_codes:  # Enregistre uniquement les sous-domaines valides
                        scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        result = (domain, subdomain, http_codes, ports, ip_address, scan_time)
                        f.write(','.join(result) + '\n')
                except Exception as e:
                    print(f"Erreur lors du traitement de {futures[future]} : {str(e)}")
