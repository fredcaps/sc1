import subprocess
import concurrent.futures
from utils import print_message

def run_tool(command, tool_name):
    try:
        print_message(f"Lancement de {tool_name} en mode passif...", symbol="=")
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print_message(f"Fin de {tool_name}", symbol="-")
        return result.stdout.splitlines()
    except Exception as e:
        print(f"Erreur lors de l'exécution de {tool_name} : {str(e)}")
        return []

def clean_subdomain(subdomain, domain):
    """
    Nettoie les sous-domaines, en particulier pour les résultats complexes d'Amass.
    """
    # Traite les cas où Amass inclut des flèches ou des informations supplémentaires
    if " --> " in subdomain:
        subdomain = subdomain.split(" --> ")[-1]  # Ne garder que la dernière partie du sous-domaine

    # Nettoie les sous-domaines pour éviter les espaces ou caractères inattendus
    subdomain = subdomain.strip()

    # Vérifier que le sous-domaine appartient bien au domaine principal
    if subdomain.endswith(f".{domain}"):
        return subdomain
    else:
        print(f"Filtrage: {subdomain} n'appartient pas à {domain}")
        return None

def collect_subdomains(domain, tools):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(run_tool, tool(domain), tool_name): tool_name for tool_name, tool in tools.items()}
        subdomains = set()
        for future in concurrent.futures.as_completed(futures):
            tool_name = futures[future]
            try:
                result = future.result()
                for subdomain in result:
                    cleaned_subdomain = clean_subdomain(subdomain, domain)
                    if cleaned_subdomain:
                        subdomains.add(cleaned_subdomain)
            except Exception as e:
                print(f"Erreur avec {tool_name}: {str(e)}")

    return list(subdomains)
