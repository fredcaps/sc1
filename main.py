#!/usr/bin/env python

import subprocess
import argparse
import time
from datetime import datetime
import os
from tools import collect_subdomains
from results import filter_and_write_results
from utils import print_message
# Importer le module database
import database

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

    for domain in domains:
        subdomains = collect_subdomains(domain, tools)
        filter_and_write_results(subdomains, domain, output_file)
        print(f"Résultats pour {domain} enregistrés dans {output_file}")

    duration = time.time() - start_time
    print_message(f"Le script s'est terminé en {duration:.2f} secondes.", symbol="#")
    print_message(f"Intégration des résultats dans la base de données", symbol="#")
    print(f"Nom du fichier généré : {output_file}")
    # Appeler la fonction pour insérer les résultats dans la base de données
    database.insert_results_from_file(output_file)
    print_message(f"L'intégration dans la base de données est terminée", symbol="#")

if __name__ == "__main__":
    main()
