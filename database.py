import psycopg2
import csv
from utils import print_message

# Fonction pour se connecter à la base de données
def connect_db():
    try:
        connection = psycopg2.connect(
            database="scans",     # Nom de la base de données
            user="scanner",       # Nom d'utilisateur PostgreSQL
            password="password",  # Mot de passe PostgreSQL
            host="localhost",     # Adresse du serveur PostgreSQL
            port="5432"           # Port PostgreSQL
        )
        return connection
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données: {str(e)}")
        return None

# Fonction pour obtenir le prochain scan_id
def get_next_scan_id():
    connection = connect_db()
    if connection is None:
        return None

    cursor = connection.cursor()
    cursor.execute("SELECT MAX(scan_id) FROM scan_results")
    result = cursor.fetchone()
    connection.close()

    # Si aucun scan n'existe encore, retourner 1
    return (result[0] + 1) if result[0] is not None else 1

# Fonction pour insérer les résultats de scan dans la base de données
def insert_results_from_file(output_file):
    scan_id = get_next_scan_id()
    if scan_id is None:
        print("Impossible d'obtenir un scan_id valide.")
        return

    connection = connect_db()
    if connection is None:
        return

    cursor = connection.cursor()

    try:
        with open(output_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 6:
                    print(f"Ligne incorrecte dans le fichier : {row}")
                    continue
                domain, subdomain, http_codes, ports, ip_address, scan_time = row
                cursor.execute("""
                    INSERT INTO scan_results (scan_id, domain, subdomain, http_codes, ports, ip_address, scan_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (scan_id, domain, subdomain, http_codes, ports, ip_address, scan_time))
        connection.commit()
        print(f"Résultats insérés avec succès dans la base de données avec scan_id = {scan_id}")
    except Exception as e:
        print(f"Erreur lors de l'insertion des résultats : {str(e)}")
    finally:
        connection.close()
