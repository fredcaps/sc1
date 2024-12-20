import sys
import base64
import subprocess
import os
import glob
import time
from concurrent.futures import ThreadPoolExecutor

# Fonction pour capturer une page avec Aquatone et convertir en Base64
def capture_aquatone(subdomain, port):
    max_attempts = 2  # Nombre maximum de tentatives
    delay_between_attempts = 3  # Intervalle en secondes entre les tentatives

    for attempt in range(max_attempts):
        try:
            # Spécifier un répertoire de sortie pour stocker les captures
            output_dir = f"./captures/{subdomain}_{port}"
            os.makedirs(output_dir, exist_ok=True)

            # Appel d'Aquatone pour capturer la page
            aquatone_cmd = f"echo {subdomain} | aquatone -ports {port} -out {output_dir}"
            subprocess.run(aquatone_cmd, shell=True, check=True)

            # Chercher les fichiers PNG dans le dossier screenshots
            screenshot_pattern = f"{output_dir}/screenshots/*.png"
            screenshots = glob.glob(screenshot_pattern)

            if screenshots:
                # Prendre le premier fichier trouvé (s'il y a plusieurs captures)
                screenshot_path = screenshots[0]
                with open(screenshot_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode("utf-8").replace("\n", "")
                return base64_image
            else:
                print(f"Pas de fichier PNG trouvé dans {output_dir}/screenshots/")
                time.sleep(delay_between_attempts)  # Attente avant la prochaine tentative
        except Exception as e:
            print(f"Erreur lors de la capture de {subdomain} sur le port {port} : {e}")
            time.sleep(delay_between_attempts)

    # Si toutes les tentatives échouent, retourner une chaîne vide
    return ""

# Fonction pour traiter un sous-domaine (HTTP/HTTPS)
def process_subdomain(row):
    # Extraction des données
    domain, subdomain, http_codes, ports, ip, date_time = row.strip().split(',')

    ports_list = ports.split("-")
    http_codes_list = http_codes.split("-")

    # Capture HTTP (port 80) sauf pour les erreurs 4xx et 5xx
    if "80" in ports_list and not any(code.startswith(("4", "5")) for code in http_codes_list):
        image_http_base64 = capture_aquatone(subdomain, "80")
    else:
        image_http_base64 = ""

    # Capture HTTPS (port 443) sauf pour les erreurs 4xx et 5xx
    if "443" in ports_list and not any(code.startswith(("4", "5")) for code in http_codes_list):
        image_https_base64 = capture_aquatone(subdomain, "443")
    else:
        image_https_base64 = ""

    # Format des images avec une virgule finale même si les images sont vides
    images_base64 = f"{image_http_base64},{image_https_base64}".replace("\n", "") if image_http_base64 or image_https_base64 else ","

    # Retourner la ligne formatée
    return f"{domain},{subdomain},{http_codes},{ports},{ip},{date_time},{images_base64}"

# Lecture du fichier TXT et multithreading avec concurrent.futures
def process_file(input_file):
    with open(input_file, "r") as infile:
        lines = infile.readlines()

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_subdomain, lines))

    # Écriture du fichier de sortie avec les résultats dans le même fichier
    with open(input_file, "w") as outfile:
        for result in results:
            outfile.write(result + "\n")

# Exemple d'exécution
if __name__ == "__main__":
    input_file = sys.argv[1]  # Utilisation du même fichier en entrée et sortie
    process_file(input_file)
