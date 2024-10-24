import subprocess
import argparse
import time
from datetime import datetime
from tools import collect_subdomains
from results import filter_and_write_results
from utils import print_message
import os
import concurrent.futures

def process_directory(directory):
    """
    Parcours tous les fichiers dans un répertoire et traite chaque fichier comme une liste de domaines.
    
    Args:
        directory (str): Chemin vers le répertoire à traiter.
    """
    domains = []
    
    # Parcours de tous les fichiers du répertoire
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Lire chaque fichier contenant des domaines
            with open(file_path, 'r', encoding='utf-8') as f:
                file_domains = f.read().splitlines()
                domains.extend(file_domains)

    return domains

def process_domain(domain, tools, output_file):
    """
    Fonction pour traiter un seul domaine (collecte des sous-domaines et écriture des résultats).
    
    Args:
        domain (str): Le domaine à traiter.
        tools (dict): Dictionnaire des outils de collecte de sous-domaines.
        output_file (str): Fichier de sortie pour enregistrer les résultats.
    """
    print(f"⚙  Traitement de {domain}...")
    subdomains = collect_subdomains(domain, tools)
    filter_and_write_results(subdomains, domain, output_file)
    print(f"⚙  Résultats pour {domain} enregistrés dans {output_file}.")

def main():
    # Message général d'exécution
    print("⚙  Exécution du script de collecte de sous-domaines et génération des rapports...")

    # Définition des arguments du script
    parser = argparse.ArgumentParser(
        description="Script de reconnaissance en mode passif",
        add_help=False  # On désactive l'aide par défaut
    )

    # Ajout manuel de l'option d'aide en français
    parser.add_argument(
        '-h', '--help', action='help', default=argparse.SUPPRESS,
        help="Afficher ce message d'aide et quitter."
    )

    # Argument pour un domaine unique avec description et metavar personnalisés
    parser.add_argument(
        "-d", metavar="DOMAIN", help="Domaine unique (ex: example.com)"
    )

    # Argument pour un fichier de domaines avec description et metavar personnalisés
    parser.add_argument(
        "-fd", metavar="FILE", help="Fichier contenant une liste de domaines"
    )
    
    # Argument pour un répertoire contenant des fichiers de domaines
    parser.add_argument(
        "-dr", metavar="DIRECTORY", help="Répertoire contenant plusieurs fichiers de domaines"
    )

    # Argument pour générer un rapport minimaliste
    parser.add_argument(
        "--minimaliste", action="store_true", help="Générer un rapport minimaliste au lieu des rapports complets"
    )

    args = parser.parse_args()

    # Si aucun argument n'est passé, afficher un message d'aide
    if not args.d and not args.fd and not args.dr:
        parser.print_help()  # Affiche le message d'aide
        print("\n⚠  Erreur : Vous devez fournir soit un domaine avec l'option -d, soit un fichier avec l'option -fd, soit un répertoire avec l'option -dr.\n")
        return

    # Outils de collecte de sous-domaines
    tools = {
        "findomain": lambda domain: ["findomain", "-t", domain],
        "assetfinder": lambda domain: ["assetfinder", domain],
        # "amass": lambda domain: ["amass", "enum", "-passive", "-d", domain],  # Commenté
        "subfinder": lambda domain: ["subfinder", "-d", domain]               # Commenté
    }

    # Vérification des domaines
    if args.d:
        domains = [args.d]
    elif args.fd and os.path.exists(args.fd):
        with open(args.fd) as f:
            domains = f.read().splitlines()
    elif args.dr and os.path.isdir(args.dr):
        domains = process_directory(args.dr)  # Traiter tous les fichiers du répertoire
    else:
        print("Veuillez fournir un domaine avec -d, un fichier avec -fd, ou un répertoire avec -dr.")
        return

    # Début du traitement
    start_time = time.time()
    output_file = f"Scan_du_{datetime.now().strftime('%Y-%m-%d_%H-%M')}_results.txt"

    # Exécution des domaines en parallèle
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_domain, domain, tools, output_file): domain for domain in domains}

        for future in concurrent.futures.as_completed(futures):
            domain = futures[future]
            try:
                future.result()  # Attendre que chaque future se termine
            except Exception as exc:
                print(f"⚠  Erreur pour le domaine {domain} : {exc}")
            else:
                print(f"⚙  Le traitement de {domain} est terminé.")

    # Durée d'exécution
    duration = time.time() - start_time
    print_message(f"⚙  Le script s'est terminé en {duration:.2f} secondes.")

    # Si l'argument minimaliste est passé, exécuter rapport_minimaliste.py
    if args.minimaliste:
        try:
            print("⚙  Exécution du script rapport_minimaliste.py...")
            subprocess.run(["python", "rapport_minimaliste.py", output_file, "-o", "Rapport_minimaliste"], check=True)
            print(f"⚙  Le script rapport_minimaliste.py a été exécuté avec succès avec le fichier {output_file}.")
        except subprocess.CalledProcessError as e:
            print(f"⚠  Erreur lors de l'exécution de rapport_minimaliste.py : {str(e)}")
    else:
        # Si l'argument minimaliste n'est PAS passé, exécuter database.py et Generateur_rapport.py
        try:
            print("⚙  Exécution du script database.py avec le fichier généré...")
            subprocess.run(["python", "database.py", output_file], check=True)
            print(f"⚙  Le script database.py a été exécuté avec succès avec le fichier {output_file}.")
        except subprocess.CalledProcessError as e:
            print(f"⚠  Erreur lors de l'exécution de database.py : {str(e)}")

        # Exécution du script Generateur_rapport.py
        try:
            print("⚙  Exécution du script Generateur_rapport.py...")
            subprocess.run(["python", "Generateur_rapport.py"], check=True)
            print("⚙  Le script Generateur_rapport.py a été exécuté avec succès.")
        except subprocess.CalledProcessError as e:
            print(f"⚠  Erreur lors de l'exécution de Generateur_rapport.py : {str(e)}")

if __name__ == "__main__":
    main()