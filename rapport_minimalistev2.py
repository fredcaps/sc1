import os
from datetime import datetime
import pytz
import argparse

def read_scan_results(file_path):
    """
    Lit les résultats de scan à partir d'un fichier texte sans en-têtes.
    
    Args:
        file_path (str): Chemin vers le fichier texte contenant les résultats de scan.

    Returns:
        list of tuples: Liste des résultats de scan sous forme de tuples.
    """
    scans = []
    try:
        with open(file_path, 'r', encoding='utf-8') as txtfile:
            for line in txtfile:
                # Supposer que chaque ligne contient les 6 colonnes attendues
                data = line.strip().split(',')
                if len(data) != 6:
                    print(f"Ligne mal formatée: {line}")
                    continue
                
                try:
                    # Extraire les données de chaque ligne sans se baser sur des en-têtes
                    domain = data[0].strip()
                    subdomain = data[1].strip()
                    http_code = data[2].strip()  # Conserver les tirets dans les codes HTTP
                    port = data[3].strip()  # Conserver les tirets dans les ports
                    ip_address = data[4].strip()

                    # Conversion de scan_time en objet datetime avec timezone UTC
                    scan_time = datetime.strptime(data[5], "%Y-%m-%d %H:%M:%S")
                    scan_time = pytz.utc.localize(scan_time)

                    # Ajouter les résultats dans la liste sans validation
                    scans.append((domain, subdomain, http_code, port, ip_address, scan_time))
                except ValueError as ve:
                    print(f"Erreur de format de la ligne {line}: {ve}")
    except FileNotFoundError:
        print(f"Fichier non trouvé : {file_path}")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {str(e)}")
    
    return scans

def generate_html_report(scans, output_dir="rapport_scans"):
    """
    Génère un rapport HTML à partir des résultats de scan.

    Args:
        scans (list of tuples): Liste des résultats de scan.
        output_dir (str): Répertoire où le rapport sera enregistré.
    """
    # Convertir l'heure en heure de Montréal
    montreal_tz = pytz.timezone('America/Montreal')

    # Calculer les statistiques globales
    total_scans = len(set([scan[0] for scan in scans]))
    total_subdomains = len(set([scan[1] for scan in scans]))
    total_domains = len(set([scan[0] for scan in scans]))

    # Générer l'entête du rapport avec le bon design pour les statistiques
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Rapport de Scan</title>
        <style>
            body {{
                font-family: 'Roboto', sans-serif;
                margin: 20px;
                background-color: #f9f9f9;
                color: #333;
            }}
            h1, h2, h3 {{
                color: #4CAF50;
            }}
            .stat-box {{
                padding: 10px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                background-color: #f1f1f1;
                color: #4CAF50;
                font-weight: bold;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                text-align: center;
                width: fit-content;
                display: inline-block;
                margin-right: 15px;
            }}
            .stats {{
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
                justify-content: flex-start;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
            }}
        </style>
    </head>
    <body>
        <h1>Rapport de Scan du {datetime.now(montreal_tz).strftime("%Y-%m-%d à %H:%M")}</h1>
        <div class="stats">
            <div class="stat-box">Total de Scans: {total_scans}</div>
            <div class="stat-box">Total de Sous-domaines Scannés: {total_subdomains}</div>
            <div class="stat-box">Total de Domaines Scannés: {total_domains}</div>
        </div>
        <h2>Résultats des Scans</h2>
        <table>
            <tr>
                <th>Domaine</th>
                <th>Sous-domaine</th>
                <th>Code HTTP</th>
                <th>Port</th>
                <th>Adresse IP</th>
                <th>Heure du Scan</th>
            </tr>
    """

    # Ajouter les lignes du tableau
    for scan in scans:
        domain, subdomain, http_code, port, ip_address, scan_time = scan
        scan_time_local = scan_time.astimezone(montreal_tz).strftime("%Y-%m-%d %H:%M:%S")

        html += f"""
            <tr>
                <td>{domain}</td>
                <td>{subdomain}</td>
                <td>{http_code}</td>
                <td>{port}</td>
                <td>{ip_address}</td>
                <td>{scan_time_local}</td>
            </tr>
        """

    # Clôturer le tableau et le corps du HTML
    html += """
        </table>
    </body>
    </html>
    """

    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Générer le nom de fichier avec la date et l'heure actuelles
    current_time = datetime.now(montreal_tz).strftime("%Y-%m-%d-%H-%M")
    filename = os.path.join(output_dir, f"rapport_scans_{current_time}.html")

    # Écrire le rapport HTML dans le fichier
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)

    # Afficher un message avec le lien et le nom du fichier généré
    print(f"Génération terminée ! Le rapport a été enregistré sous le nom : {filename}")

def main():
    """
    Fonction principale pour lire les résultats de scan à partir d'un fichier texte et générer un rapport HTML.
    """
    parser = argparse.ArgumentParser(description="Générateur de rapport de scans à partir d'un fichier texte.")
    parser.add_argument("input_file", help="Chemin vers le fichier texte sans en-têtes contenant les résultats de scan.")
    parser.add_argument("-o", "--output_dir", default="rapport_scans", help="Répertoire de sortie pour le rapport HTML.")

    args = parser.parse_args()

    # Lire les résultats de scan depuis le fichier texte
    scans = read_scan_results(args.input_file)
    if not scans:
        print("Aucun scan trouvé ou erreur lors de la lecture du fichier.")
        return

    # Générer le rapport HTML
    generate_html_report(scans, args.output_dir)

if __name__ == "__main__":
    main()
