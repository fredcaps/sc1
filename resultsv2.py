import concurrent.futures
from datetime import datetime
from network import get_http_ports_and_ip

def filter_and_write_results(subdomains, domain, output_file):
    # Génère le nom du fichier des sous-domaines invalides en fonction du fichier valide
    invalid_output_file = f"invalide_{output_file}"
    
    unique_subdomains = set(subdomains)
    
    # Ouverture de deux fichiers : un pour les sous-domaines valides et un pour les non valides
    with open(output_file, 'a') as valid_file, open(invalid_output_file, 'a') as invalid_file:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(get_http_ports_and_ip, subdomain): subdomain for subdomain in unique_subdomains}
            
            for future in concurrent.futures.as_completed(futures):
                subdomain, http_codes, ports, ip_address = future.result()
                
                # Si le sous-domaine est valide (pas de "N/A" dans les codes HTTP)
                if "N/A" not in http_codes:
                    valid_file.write(f"{domain},{subdomain},{http_codes},{ports},{ip_address},{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                else:
                    # Si le sous-domaine n'est pas valide, on l'écrit dans le fichier des sous-domaines non valides
                    invalid_file.write(f"{domain},{subdomain},N/A,N/A,N/A,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

