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

# Fonction pour obtenir le prochain scan_id
def get_next_scan_id():
    connection = connect_db()
    if connection is None:
        return None

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(scan_id) FROM scan_results")
        result = cursor.fetchone()
        connection.close()

        # Si aucun scan n'existe encore, retourner 1
        return (result[0] + 1) if result[0] is not None else 1
    except Exception as e:
        print(f"Erreur lors de la récupération du prochain scan_id: {str(e)}")
        connection.close()
        return None

# Fonction pour insérer les résultats de scan dans la base de données
def insert_scan_result(scan_id, domain, subdomain, http_codes, ports, ip_address, scan_time):
    connection = connect_db()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO scan_results (scan_id, domain, subdomain, http_codes, ports, ip_address, scan_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (scan_id, domain, subdomain, http_codes, ports, ip_address, scan_time))

        connection.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des données: {str(e)}")
    finally:
        connection.close()
