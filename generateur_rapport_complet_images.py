import os
import psycopg2
from datetime import datetime
import pytz
import argparse

# Fonction principale
def main():
    # Utilisation d'argparse pour gérer les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Générateur de rapport de scan")
    parser.add_argument("-o", "--output_directory", default="rapport_scans", help="Répertoire de sortie pour le rapport")
    parser.add_argument("-f", "--output_file", help="Nom du fichier de sortie (avec extension .html)")
    args = parser.parse_args()

    output_directory = args.output_directory
    output_file_name = args.output_file

    # Connexion à la base de données
    conn = psycopg2.connect(
        dbname="scans",         # Nom de votre base de données actuelle
        user="scanner",         # Votre utilisateur PostgreSQL
        password="password",    # Mot de passe PostgreSQL
        host="localhost"
    )
    cur = conn.cursor()

    # Récupération de tous les scans (sélection explicite des colonnes)
    cur.execute("""
        SELECT scan_id, domain, subdomain, http_codes, ports, ip_address, scan_time, image_http_base64, image_https_base64
        FROM scan_results
        ORDER BY scan_id DESC, scan_time DESC
    """)
    scans = cur.fetchall()

    # Générer le rapport HTML
    generate_html_report(scans, output_directory, output_file_name)

    # Fermer la connexion à la base de données
    cur.close()
    conn.close()

# Fonction pour générer le rapport HTML
def generate_html_report(scans, output_directory, output_file_name):
    # Convertir l'heure en heure de Montréal
    montreal_tz = pytz.timezone('America/Montreal')
    image_counter = 0  # Compteur pour les IDs uniques des images

    # Calculer les statistiques globales
    total_scans = len(set(scan[0] for scan in scans))
    total_subdomains = len(set(scan[2] for scan in scans))
    total_domains = len(set(scan[1] for scan in scans))

    # Déterminer le titre du rapport et le nom du fichier
    current_time = datetime.now(montreal_tz).strftime("%Y-%m-%d à %H:%M")
    if output_file_name:
        filename = output_file_name
        title_text = os.path.splitext(output_file_name)[0]
    else:
        current_time_filename = datetime.now(montreal_tz).strftime("%Y-%m-%d-%H-%M")
        filename = f"rapport_scans_{current_time_filename}.html"
        title_text = f"Rapport de Scan du {current_time}"

    # Générer l'entête du rapport avec le bon design pour les statistiques
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
            .added {{
                background-color: lightgreen;
            }}
            .removed {{
                background-color: lightcoral;
            }}
            .modified {{
                background-color: lightyellow;
            }}
            .unchanged {{
                background-color: lightgray;
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
            .legend-table {{
                width: 50%;
                margin: 20px auto;
                border: 1px solid #ddd;
                text-align: center;
            }}
            .legend-table td {{
                padding: 10px;
                font-weight: bold;
            }}
            .old-value {{
                color: red;
                font-weight: bold;
            }}
            .new-value {{
                color: green;
                font-weight: bold;
            }}
            .image-container {{
                margin-top: 10px;
            }}
            .image-container img {{
                max-width: 100%;
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
        <h3>Légende des Codes Couleurs</h3>
        <table class="legend-table">
            <tr>
                <td style="background-color: lightgreen;">Ajouté</td>
                <td style="background-color: lightyellow;">Modifié</td>
                <td style="background-color: lightcoral;">Supprimé</td>
                <td style="background-color: lightgray;">Déjà présent</td>
            </tr>
        </table>
        <div class="stats">
            <div class="stat-box">Total de Scans: {total_scans}</div>
            <div class="stat-box">Total de Sous-domaines Scannés: {total_subdomains}</div>
            <div class="stat-box">Total de Domaines Scannés: {total_domains}</div>
        </div>
    """

    scan_data = {}
    for scan in scans:
        # Assurer que le déballage correspond au nombre de colonnes récupérées
        scan_id, domain, subdomain, http_code, port, ip_address, scan_time, image_http, image_https = scan
        if scan_id not in scan_data:
            scan_data[scan_id] = []
        scan_data[scan_id].append((domain, subdomain, http_code, port, ip_address, scan_time, image_http, image_https))

    sorted_scan_ids = sorted(scan_data.keys(), reverse=True)
    for i, scan_id in enumerate(sorted_scan_ids):
        current_scan = scan_data[scan_id]
        previous_scan = scan_data[sorted_scan_ids[i + 1]] if i + 1 < len(sorted_scan_ids) else []

        # Initialisation des ajouts, modifications et suppressions pour chaque scan
        additions = 0
        modifications = 0
        deletions = 0

        # Compte des sous-domaines du scan actuel
        current_subdomains_count = len(current_scan)

        previous_scan_dict = {
            (domain, subdomain): (http_code, port, ip_address, image_http, image_https)
            for domain, subdomain, http_code, port, ip_address, scan_time, image_http, image_https in previous_scan
        }

        # Parcourir le scan actuel pour compter les ajouts et les modifications
        current_scan_keys = set()
        for domain, subdomain, http_code, port, ip_address, scan_time, image_http, image_https in current_scan:
            key = (domain, subdomain)
            current_scan_keys.add(key)
            if key not in previous_scan_dict:
                additions += 1
            elif (
                http_code != previous_scan_dict[key][0]
                or port != previous_scan_dict[key][1]
                or ip_address != previous_scan_dict[key][2]
            ):
                modifications += 1

        # Compter les suppressions en comparant avec le scan précédent
        for domain, subdomain in previous_scan_dict:
            if (domain, subdomain) not in current_scan_keys:
                deletions += 1

        # Maintenant que les compteurs sont calculés, insérez-les dans le HTML
        html += f"""
        <div class="scan-result">
            <h2>Rapport du Scan ID: {scan_id}</h2>
            <h3>Date: {current_scan[0][5].astimezone(montreal_tz).strftime("%Y-%m-%d %H:%M:%S")}</h3>
            <div class="stats">
                <div class="stat-box">Sous-domaines: {current_subdomains_count}</div>
                <div class="stat-box">Ajouts: {additions}</div>
                <div class="stat-box">Modifications: {modifications}</div>
                <div class="stat-box">Suppressions: {deletions}</div>
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
                    <th>Image HTTP</th>
                    <th>Image HTTPS</th>
                </tr>
        """

        # Générer les lignes du tableau avec les classes appropriées
        for domain, subdomain, http_code, port, ip_address, scan_time, image_http, image_https in current_scan:
            key = (domain, subdomain)
            if key not in previous_scan_dict:
                # Ajouté
                row_class = "added"
            elif (
                http_code != previous_scan_dict[key][0]
                or port != previous_scan_dict[key][1]
                or ip_address != previous_scan_dict[key][2]
            ):
                # Modifié
                row_class = "modified"
            else:
                # Inchangé
                row_class = "unchanged"

            # Générer les boutons et images pour HTTP
            if image_http:
                image_counter += 1
                img_http_id = f"img_http_{image_counter}"
                image_http_html = f"""
                <button onclick="toggleImage('{img_http_id}')">Voir Image HTTP</button>
                <div class="image-container">
                    <img id="{img_http_id}" src="data:image/png;base64,{image_http}" style="display:none;"/>
                </div>
                """
            else:
                image_http_html = "N/A"

            # Générer les boutons et images pour HTTPS
            if image_https:
                image_counter += 1
                img_https_id = f"img_https_{image_counter}"
                image_https_html = f"""
                <button onclick="toggleImage('{img_https_id}')">Voir Image HTTPS</button>
                <div class="image-container">
                    <img id="{img_https_id}" src="data:image/png;base64,{image_https}" style="display:none;"/>
                </div>
                """
            else:
                image_https_html = "N/A"

            # Comparer les valeurs précédentes pour les modifications
            if row_class == "modified":
                prev_http_code, prev_port, prev_ip_address, _, _ = previous_scan_dict[key]

                http_code_display = f"{prev_http_code} &rarr; <span class='new-value'>{http_code}</span>" if http_code != prev_http_code else f"{http_code}"
                port_display = f"{prev_port} &rarr; <span class='new-value'>{port}</span>" if port != prev_port else f"{port}"
                ip_address_display = f"{prev_ip_address} &rarr; <span class='new-value'>{ip_address}</span>" if ip_address != prev_ip_address else f"{ip_address}"
            else:
                http_code_display = f"{http_code}"
                port_display = f"{port}"
                ip_address_display = f"{ip_address}"

            html += f"""
            <tr class="{row_class}">
                <td>{domain}</td>
                <td>{subdomain}</td>
                <td>{http_code_display}</td>
                <td>{port_display}</td>
                <td>{ip_address_display}</td>
                <td>{scan_time.astimezone(montreal_tz).strftime("%Y-%m-%d %H:%M:%S")}</td>
                <td>{image_http_html}</td>
                <td>{image_https_html}</td>
            </tr>
            """

        # Ajouter les suppressions
        for domain, subdomain in previous_scan_dict:
            if (domain, subdomain) not in current_scan_keys:
                # Suppression
                prev_http_code, prev_port, prev_ip_address, prev_image_http, prev_image_https = previous_scan_dict[(domain, subdomain)]
                # Générer les images N/A pour les suppressions
                image_http_html = "N/A"
                image_https_html = "N/A"
                html += f"""
                <tr class="removed">
                    <td>{domain}</td>
                    <td>{subdomain}</td>
                    <td>{prev_http_code}</td>
                    <td>{prev_port}</td>
                    <td>{prev_ip_address}</td>
                    <td></td>
                    <td>{image_http_html}</td>
                    <td>{image_https_html}</td>
                </tr>
                """

        html += """
        </table>
        </div>
        """

    html += """
    </body>
    </html>
    """

    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Chemin complet du fichier de sortie
    output_path = os.path.join(output_directory, filename)

    # Écrire le rapport HTML dans le fichier
    with open(output_path, "w") as file:
        file.write(html)

    # Afficher un message avec le lien et le nom du fichier généré
    print(f"Génération terminée ! Le rapport a été enregistré sous le nom : {output_path}")

if __name__ == "__main__":
    main()

