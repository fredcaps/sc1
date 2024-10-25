
# Tutoriel : Installation des Outils et Modules pour le Projet 

## 1. Mise à Jour du Système

Avant de commencer, assurez-vous que votre système est à jour en exécutant la commande suivante :

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 2. Installer Python et les Dépendances Python

Installez Python et le gestionnaire de paquets `pip` :

```bash
sudo apt install python3 python3-pip -y
```

Ensuite, installez les bibliothèques Python requises pour les connexions à la base de données, la gestion des fuseaux horaires et les requêtes HTTP :

```bash
pip install psycopg2-binary pytz requests
```

---

## 3. Installer les Outils Externes

### 3.1. Installation de Findomain

Téléchargez et installez Findomain avec les commandes suivantes :

```bash
wget https://github.com/findomain/findomain/releases/download/4.0.0/findomain-linux  
chmod +x findomain-linux  
sudo mv findomain-linux /usr/local/bin/findomain
```

---

### 3.2. Installation de Subfinder

Assurez-vous d'avoir Go installé. Si ce n'est pas le cas, installez-le avec :

```bash
sudo apt install golang-go -y
```

Ensuite, installez Subfinder :

```bash
GO111MODULE=on go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

---

### 3.3. Installation d'Assetfinder

Installez Assetfinder en utilisant la commande suivante :

```bash
go install github.com/tomnomnom/assetfinder@latest
```

---

### 3.4. Installation de Amass

Installez Amass avec la commande suivante :

```bash
sudo apt install amass -y
```

---

### 3.5. Installation d'Aquatone

Aquatone n’est pas disponible dans les dépôts classiques, installez-le manuellement avec les commandes suivantes :

1. **Téléchargez Aquatone depuis le dépôt GitHub :**

   ```bash
   wget https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip
   ```

2. **Décompressez le fichier téléchargé :**

   ```bash
   unzip aquatone_linux_amd64_1.7.0.zip
   ```

3. **Rendez le fichier exécutable et déplacez-le dans un répertoire accessible :**

   ```bash
   chmod +x aquatone
   sudo mv aquatone /usr/local/bin/
   ```

---

## 4. Vérification des Installations

Après avoir installé chaque outil, vérifiez que tout fonctionne correctement en exécutant les commandes suivantes :

```bash
findomain --version  
subfinder --version  
assetfinder --version  
amass -version
aquatone --version
```

---

## 5. Exécution du Script Principal

Une fois les outils et modules installés, vous pouvez exécuter le script principal avec la commande suivante :

```bash
python3 main.py
```

---

Ce guide couvre l'installation et la configuration des outils et modules nécessaires pour le bon fonctionnement du projet.
