import os
from datetime import datetime
import pytz
import argparse

# Fonction pour générer le nom du fichier rapport
def generate_report_filename():
    montreal_tz = pytz.timezone('America/Montreal')
    current_time = datetime.now(montreal_tz).strftime("%Y-%m-%d-%H-%M")
    filename = f"rapport_scans_{current_time}.html"
    return filename

# Fonction pour créer un dossier s'il n'existe pas
def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Fonction pour lire le fichier .txt avec les sous-domaines
def read_input_file(input_file):
    entries = []
    with open(input_file, 'r') as file:
        for line in file:
            # Chaque ligne est supposée avoir la structure: domain, subdomain, http_codes, ports, ip_address, scan_time, image_http_base64, image_https_base64
            parts = line.strip().split(',')
            if len(parts) == 8:
                entries.append({
                    'domain': parts[0],
                    'subdomain': parts[1],
                    'http_codes': parts[2],
                    'ports': parts[3],
                    'ip_address': parts[4],
                    'scan_time': parts[5],
                    'image_http': parts[6],  # image_http_base64
                    'image_https': parts[7]  # image_https_base64
                })
            else:
                print(f"Problème avec la ligne : {line.strip()}")  # Debug si la ligne est incorrecte
    return entries

# Fonction pour générer le rapport HTML
def generate_html_report(entries, output_directory, output_file_name):
    montreal_tz = pytz.timezone('America/Montreal')
    image_counter = 0  # Compteur pour les IDs uniques des images

    total_scans = len(set(entry['scan_time'] for entry in entries))
    total_subdomains = len(set(entry['subdomain'] for entry in entries))
    total_domains = len(set(entry['domain'] for entry in entries))

    # Prendre l'heure actuelle pour afficher dans le titre
    current_time = datetime.now(montreal_tz).strftime("%Y-%m-%d à %H:%M")

    # Déterminer le nom du fichier et le titre du rapport
    if output_file_name:
        filename = output_file_name
        title_text = os.path.splitext(output_file_name)[0]
    else:
        filename = generate_report_filename()
        title_text = f"Rapport de Scan du {current_time}"

    # Générer l'entête du rapport avec la date et l'heure
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>{title_text}</title>
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
            .scan-result {{
                border: 1px solid #ddd;
                padding: 10px;
                margin-bottom: 20px;
                border-radius: 5px;
                background-color: #fff;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
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
            img {{
                max-width: 600px;
                max-height: 600px;
                width: auto;
                height: auto;
            }}
        </style>
        <script>
            function toggleImage(id) {{
                var img = document.getElementById(id);
                if (img.style.display === "none") {{
                    img.style.display = "block";
                }} else {{
                    img.style.display = "none";
                }}
            }}
        </script>
    </head>
    <body>
        <h1>{title_text}</h1>
        <div class="stats">
            <div class="stat-box">Total de Scans: {total_scans}</div>
            <div class="stat-box">Total de Sous-domaines Scannés: {total_subdomains}</div>
            <div class="stat-box">Total de Domaines Scannés: {total_domains}</div>
        </div>
        <table>
            <tr>
                <th>Domaine</th>
                <th>Sous-domaine</th>
                <th>Code HTTP</th>
                <th>Port</th>
                <th>Adresse IP</th>
                <th>Heure du Scan</th>
                <th>Image HTTP</th>
                <th>Image HTTPS</th>
            </tr>
    """

    for entry in entries:
        image_counter += 1
        img_http_id = f"img_http_{image_counter}"
        img_https_id = f"img_https_{image_counter + 1}"

        image_http_html = f"""
        <button onclick="toggleImage('{img_http_id}')">Voir Image HTTP</button>
        <div class="image-container">
            <img id="{img_http_id}" src="data:image/png;base64,{entry['image_http']}" style="display:none;"/>
        </div>
        """ if entry['image_http'] else "N/A"

        image_https_html = f"""
        <button onclick="toggleImage('{img_https_id}')">Voir Image HTTPS</button>
        <div class="image-container">
            <img id="{img_https_id}" src="data:image/png;base64,{entry['image_https']}" style="display:none;"/>
        </div>
        """ if entry['image_https'] else "N/A"

        html += f"""
        <tr>
            <td>{entry['domain']}</td>
            <td>{entry['subdomain']}</td>
            <td>{entry['http_codes']}</td>
            <td>{entry['ports']}</td>
            <td>{entry['ip_address']}</td>
            <td>{entry['scan_time']}</td>
            <td>{image_http_html}</td>
            <td>{image_https_html}</td>
        </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    # Créer le répertoire de sortie s'il n'existe pas
    create_directory_if_not_exists(output_directory)

    # Écrire le rapport HTML dans le fichier
    output_path = os.path.join(output_directory, filename)
    with open(output_path, "w") as file:
        file.write(html)

    print(f"Génération terminée ! Le rapport a été enregistré sous le nom : {output_path}")

# Point d'entrée principal
def main():
    # Utilisation d'argparse pour passer le fichier en paramètre
    parser = argparse.ArgumentParser(description="Générateur de rapport minimaliste")
    parser.add_argument("input_file", help="Chemin du fichier .txt contenant les données des sous-domaines")
    parser.add_argument("-o", "--output_directory", default="rapport_minimaliste_scans", help="Répertoire de sortie pour le rapport")
    parser.add_argument("-f", "--output_file", help="Nom du fichier de sortie (avec extension .html)")
    args = parser.parse_args()

    # Lire les données du fichier .txt
    entries = read_input_file(args.input_file)

    # Générer le rapport minimaliste
    generate_html_report(entries, args.output_directory, args.output_file)

if __name__ == "__main__":
    main()

