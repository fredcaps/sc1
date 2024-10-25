
# Tutoriel : Installation de PostgreSQL, Configuration avec Informations Personnalisées et Modifications de Code

## 1. Installer PostgreSQL

Avant de commencer, vous devez installer PostgreSQL sur votre machine. Utilisez la commande suivante en fonction de votre système d'exploitation.

### Sur Debian/Ubuntu

> sudo apt update
> sudo apt install postgresql postgresql-contrib

### Sur CentOS/RHEL

> sudo yum install postgresql-server postgresql-contrib
> sudo postgresql-setup initdb
> sudo systemctl start postgresql

### Sur macOS (Homebrew)

> brew install postgresql
> brew services start postgresql

---

## 2. Se Connecter en Tant que Superutilisateur postgres

> sudo -i -u postgres

---

## 3. Créer une Base de Données avec un Propriétaire

Nous allons créer une base de données en utilisant les informations personnalisées suivantes :

- Nom de la base de données : `scans`
- Utilisateur PostgreSQL : `scanner`
- Mot de passe : `password`

> CREATE DATABASE scans OWNER scanner;

---

## 4. Se Connecter à la Base de Données

> psql -d scans

---

## 5. Supprimer une Table Existante (Si Elle Existe)

> DROP TABLE IF EXISTS scan_results;

---

## 6. Créer une Nouvelle Table scan_results

CREATE TABLE scan_results (
    scan_id INTEGER,
    domain VARCHAR(255) NOT NULL,
    subdomain VARCHAR(255),
    http_codes VARCHAR(50),
    ports VARCHAR(50),
    ip_address INET,
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_http_base64 TEXT,
    image_https_base64 TEXT
);


---

## 7. Accorder les Permissions à l'Utilisateur scanner

> GRANT SELECT, INSERT, UPDATE ON scan_results TO scanner;

---

## 8. Vérifier la Configuration

> \d scan_results

---

## 9. Quitter psql et le Mode Superutilisateur

> \q
> exit

---

## 10. Modifications de Code dans database.py

Dans le fichier `database.py`, modifiez la fonction de connexion à la base de données pour qu'elle utilise les informations suivantes :

```python
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
```

---

## 11. Modifications de Code dans generateur_rapport_complet_images.py

Dans le fichier `generateur_rapport_complet_images.py`, remplacez la connexion à la base de données par le code suivant, en utilisant les informations personnalisées :

```python
# Connexion à la base de données
conn = psycopg2.connect(
    dbname="scans",         # Nom de votre base de données actuelle
    user="scanner",         # Votre utilisateur PostgreSQL
    password="password",    # Mot de passe PostgreSQL
    host="localhost"
)
cur = conn.cursor()
```

---

Ce guide vous permet de **installer PostgreSQL**, configurer une base de données avec des informations personnalisées, et modifier les fichiers de connexion dans `database.py` et `generateur_rapport_complet_images.py`.
