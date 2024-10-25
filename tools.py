import subprocess 
import concurrent.futures

def run_tool(command, tool_name):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.splitlines()
    except Exception as e:
        return []

def clean_subdomain(subdomain, domain):
    """
    Nettoie les sous-domaines et vérifie qu'ils appartiennent bien au domaine principal.
    """
    if " --> " in subdomain:
        subdomain = subdomain.split(" --> ")[-1]  # Ne garder que la dernière partie du sous-domaine

    subdomain = subdomain.strip()

    if subdomain.endswith(f".{domain}") or subdomain == domain:
        return subdomain
    else:
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
                pass
    
    return list(subdomains)

