
# README : Outil de Collecte et Analyse de Sous-domaines

## 1. Introduction

Cet outil permet de collecter, analyser et vérifier l'accessibilité des sous-domaines pour un domaine cible. Il utilise plusieurs outils externes pour effectuer la collecte des sous-domaines, ainsi que des vérifications réseau telles que les codes HTTP, les adresses IP et la disponibilité des ports. Des captures d’écran des sous-domaines accessibles sont également réalisées pour enrichir les rapports.

Les résultats sont stockés dans une base de données PostgreSQL pour un suivi continu, et des rapports peuvent être générés pour comparer les scans actuels avec les précédents. Un rapport spécifique pour les sous-domaines invalides ou inaccessibles est également disponible.

---

## 2. Installation et Configuration

### 2.1. Installation des outils externes

Suivez les étapes décrites dans le fichier **[Tutoriel_Installation_Outils.txt](Tutoriel_Installation_Outils.txt)** pour installer les outils externes suivants :
- `Findomain`
- `Subfinder`
- `Assetfinder`
- `Amass`
- `Aquatone` (pour les captures d’écran des sous-domaines)

### 2.2. Installation et configuration de PostgreSQL

Le fichier **[Installation_Configuration_PostgreSQL.txt](Installation_Configuration_PostgreSQL.txt)** vous guidera à travers l'installation de PostgreSQL et la création de la base de données `scans` avec les bonnes configurations.

### 2.3. Configuration du script Python

Modifiez le fichier `database.py` pour définir correctement les informations de connexion à PostgreSQL :

```python
def connect_db():
    connection = psycopg2.connect(
        database=os.getenv("DB_NAME", "scans"),        # Nom de la base de données
        user=os.getenv("DB_USER", "scanner"),          # Nom d'utilisateur PostgreSQL
        password=os.getenv("DB_PASSWORD", "password"), # Mot de passe PostgreSQL
        host=os.getenv("DB_HOST", "localhost"),        # Adresse du serveur PostgreSQL
        port=os.getenv("DB_PORT", "5432")              # Port PostgreSQL
    )
    return connection
```

---

## 3. Fonctionnement de l'Outil

### 3.1. Collecte des Sous-domaines

L'outil utilise plusieurs collecteurs de sous-domaines comme `Findomain`, `Subfinder`, `Assetfinder`, et `Amass` pour obtenir une liste complète des sous-domaines d'un domaine cible.

### 3.2. Validation des Sous-domaines

Les sous-domaines collectés sont ensuite vérifiés pour leur accessibilité. Les ports standards (80, 443) sont scannés pour déterminer la disponibilité des services HTTP et HTTPS, ainsi que d'autres informations réseau pertinentes. Ce traitement est effectué par le fichier `network.py`, qui enregistre également des captures d'écran des sous-domaines accessibles, encodées en Base64.

### 3.3. Stockage des Résultats dans PostgreSQL

Les résultats des scans (sous-domaines, adresses IP, codes HTTP) sont stockés dans une base de données PostgreSQL à l'aide du fichier `results.py`. Chaque scan est enregistré avec un identifiant unique `scan_id`.

---

## 4. Génération de Rapports

L'outil peut générer trois types de rapports :

1. **Rapport complet** : Ce rapport contient toutes les informations collectées, y compris les codes HTTP, les adresses IP, les ports, et les captures d’écran. Les résultats sont sauvegardés dans la base de données pour un suivi ultérieur. La génération de ce rapport est gérée par `generateur_rapport_complet_images.py`.

2. **Rapport minimaliste** : Ce rapport est généré sans enregistrer les données dans la base de données, permettant une visualisation rapide des résultats. Géré par `generateur_rapport_minimaliste_images.py` ou `generateur_rapport_minimaliste.py`.

3. **Rapport des sous-domaines invalides** : Ce rapport recense les sous-domaines jugés non valides ou inaccessibles, incluant les erreurs spécifiques rencontrées (exemple : erreur de résolution DNS ou code HTTP 404). Les informations sont collectées dans `results.py` et intégrées aux rapports finaux pour faciliter le suivi des sous-domaines problématiques.

---

## 5. Exécution

L'outil peut être exécuté avec les commandes suivantes :

1. Pour traiter un domaine spécifique :

   ```bash
   python3 main.py -d domaine_cible
   ```

2. Pour traiter une liste de domaines contenue dans un fichier :

   ```bash
   python3 main.py -fd fichier_de_domaines.txt
   ```

3. Pour traiter plusieurs fichiers de domaines dans un répertoire :

   ```bash
   python3 main.py -dr chemin_du_repertoire
   ```

4. Pour générer un rapport minimaliste sans sauvegarder les résultats dans la base de données :

   ```bash
   python3 main.py -d domaine_cible --minimaliste
   ```

5. Pour générer un rapport minimaliste sans sauvegarde en base de données avec une liste de domaines :

   ```bash
   python3 main.py -fd fichier_de_domaines.txt --minimaliste
   ```

6. Pour uploader un rapport vers un emplacement S3 :

   ```bash
   python3 main.py -d domaine_cible --s3_url s3://bucket/path/to/report.html
   ```

---

## 6. Remarques Supplémentaires

- **Format des fichiers d’entrée** : Les fichiers d’entrée doivent respecter les formats suivants selon le type de données à traiter :

  - **Format de base** : `domaine, sous-domaine, code HTTP, ports, adresse IP, date de scan`. Ce format est requis pour les données essentielles des sous-domaines.
  
  - **Format avec captures d’écran** : Si des images sont incluses, le format doit suivre : `domaine, sous-domaine, code HTTP, ports, adresse IP, date de scan, image_HTTP_Base64, image_HTTPS_Base64`. Les captures d’écran encodées en Base64 sont générées pour les sous-domaines accessibles et permettent un suivi visuel dans les rapports.

  Ces formats assurent une interprétation correcte des données et permettent de traiter les sous-domaines avec ou sans images.

- **Gestion des erreurs** : En cas d'erreur, vérifiez que tous les outils externes sont installés et configurés correctement, et assurez-vous que PostgreSQL est configuré comme décrit dans le guide. Pour les problèmes de connexion à la base de données, consultez et modifiez les paramètres dans `database.py` selon les informations de votre instance PostgreSQL.

---
