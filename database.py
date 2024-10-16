import os
import psycopg2

# Fonction pour se connecter à la base de données
def connect_db():
    try:
        connection = psycopg2.connect(
            database=os.getenv("DB_NAME", "scans"),        # Nom de la base de données
            user=os.getenv("DB_USER", "scanner"),          # Nom d'utilisateur PostgreSQL
            password=os.getenv("DB_PASSWORD", "password"), # Mot de passe PostgreSQL
            host=os.getenv("DB_HOST", "localhost"),        # Adresse du serveur PostgreSQL
            port=os.getenv("DB_PORT", "5432")              # Port PostgreSQL
        )
        return connection
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données: {str(e)}")
        return None

# Fonction pour lire le fichier de résultats et insérer les données dans la base de données
def insert_results_from_file(output_file):
    connection = connect_db()
    if connection is None:
        return

    try:
        cursor = connection.cursor()

        # Obtenir le prochain scan_id
        cursor.execute("SELECT MAX(scan_id) FROM scan_results")
        result = cursor.fetchone()
        scan_id = (result[0] + 1) if result[0] is not None else 1

        with open(output_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    domain, subdomain, http_codes, ports, ip_address, scan_time = line.split(',')
                    cursor.execute("""
                        INSERT INTO scan_results (scan_id, domain, subdomain, http_codes, ports, ip_address, scan_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (scan_id, domain, subdomain, http_codes, ports, ip_address, scan_time))

        connection.commit()
        print(f"Les résultats ont été insérés dans la base de données avec le scan_id {scan_id}.")

    except Exception as e:
        print(f"Erreur lors de l'insertion des données: {str(e)}")
    finally:
        connection.close()

if __name__ == "__main__":
    # Demander le nom du fichier à traiter
    output_file = input("Entrez le nom du fichier de résultats à insérer dans la base de données: ")
    if os.path.exists(output_file):
        insert_results_from_file(output_file)
    else:
        print(f"Le fichier {output_file} n'existe pas.")
