#!/usr/bin/env python

import subprocess
import argparse
import time
from datetime import datetime
import os
from tools import collect_subdomains
from results import filter_and_write_results
from utils import print_message
from database import get_next_scan_id, insert_scan_result

def main():
    parser = argparse.ArgumentParser(description="Script de reconnaissance en mode passif")
    parser.add_argument("-d", help="Domaine unique (ex: example.com)")
    parser.add_argument("-fd", help="Fichier contenant une liste de domaines")
    args = parser.parse_args()

    tools = {
        "findomain": lambda domain: ["findomain", "-t", domain],
        "assetfinder": lambda domain: ["assetfinder", domain]
    }

    if args.d:
        domains = [args.d]
    elif args.fd and os.path.exists(args.fd):
        with open(args.fd) as f:
            domains = f.read().splitlines()
    else:
        print("Veuillez fournir un domaine avec -d ou un fichier avec -fd.")
        return

    start_time = time.time()
    output_file = f"Scan_du_{datetime.now().strftime('%Y-%m-%d_%H-%M')}_results.txt"

    # Obtenir le prochain scan_id
    scan_id = get_next_scan_id()

    for domain in domains:
        subdomains = collect_subdomains(domain, tools)
        results = filter_and_write_results(subdomains, domain, output_file)

        # Insérer les résultats dans la base de données
        for result in results:
            # result est un tuple : (domain, subdomain, http_codes, ports, ip_address, scan_time)
            insert_scan_result(scan_id, *result)

        print(f"Résultats pour {domain} enregistrés dans la base de données")

    duration = time.time() - start_time
    print_message(f"Le script s'est terminé en {duration:.2f} secondes.", symbol="#")

if __name__ == "__main__":
    main()
