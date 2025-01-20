# Mlinzi Auto Backup

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Mlinzi Auto Backup est une application de bureau open-source conçue pour simplifier et automatiser la sauvegarde de bases de données MySQL.** Elle vise à fournir une solution facile à utiliser et personnalisable pour tous ceux qui ont besoin de sauvegarder leurs données régulièrement et de manière sécurisée. L'application permet de configurer la connexion à votre serveur MySQL, de sélectionner la base de données à sauvegarder, de définir le chemin de sauvegarde, de planifier des sauvegardes automatiques, d'exporter les sauvegardes, et de gérer l'ensemble du processus avec facilité.

## Fonctionnalités Clés

-   **Configuration Flexible :** Facilement configurable avec le chemin de `mysqldump`, l'hôte, le port, l'utilisateur, et le mot de passe de votre base de données MySQL.
-   **Sélection de Base de Données :** Chargement automatique des bases de données disponibles pour une sélection aisée.
-   **Gestion du Chemin de Sauvegarde :** Choisir le répertoire de destination pour vos fichiers de sauvegarde.
-   **Sauvegardes Manuelles et Automatiques :** Possibilité de lancer des sauvegardes manuelles ou de planifier des sauvegardes automatiques à intervalles réguliers en activant l'option auto backup.
-   **Gestion du temps avant la prochaine sauvegarde:** Affichage du temps avant la prochaine sauvegarde lorsque l'auto backup est activé
-   **Affichage de la progression :** Suivez l'avancement de vos sauvegardes grâce à la barre de progression intégrée.
-   **Exportation Facile :** Exportez vos sauvegardes vers n'importe quel emplacement de stockage externe.
-   **Affichage des logs :** L'application affiche les logs de chaque opération afin de comprendre le déroulement.
-   **Démarrage Automatique :** Une option permet de lancer l'application au démarrage de Windows.
-   **Bip Sonore :** Un bip sonore est joué une fois une sauvegarde terminée.
-   **Fichier de sauvegarde horodaté :** Les fichiers sont horodatés afin de mieux s'organiser.
-   **Modal d'aide :** Une fenêtre modale permet d'afficher la documentation.
   *  **Informations developpeur :** Vous trouverez mes informations en bas du modal d'aide.

## Prérequis

-   Python 3.7 ou supérieur.
-   `mysql-connector-python` (installable avec `pip install mysql-connector-python`).
-   `PyInstaller` (installable avec `pip install pyinstaller` si vous souhaitez créer un exécutable).

## Installation

1.  **Cloner le dépôt :**

    ```bash
    git clone https://github.com/votre_nom_utilisateur/mlinzi-auto-backup.git
    ```

2.  **Naviguer vers le dossier du projet :**

    ```bash
    cd mlinzi-auto-backup
    ```

3.  **Installer les dépendances :**

    ```bash
    pip install -r requirements.txt
    ```
    * Le fichier `requirements.txt` n'est pas présent, mais il est conseillé d'en créer un avec la commande `pip freeze > requirements.txt` afin que d'autre personne puisse installer les dependances.

4.  **Lancer l'application :**

    ```bash
    python main.py
    ```

**Création d'un Exécutable**
Si vous souhaitez créer un fichier executable, vous devez :
  1.   **Installer `pyinstaller` :** Si vous ne l'avez pas déjà fait, ouvrez un terminal ou une invite de commande et tapez :
        ```bash
        pip install pyinstaller
        ```
  2.   **Créer le fichier spec** Exécuter la commande :
      ```bash
      pyinstaller --windowed --icon=mlinzi_icon.ico main.py
      ```
  3. **Modifier le fichier main.spec**
      *   Ajouter les `datas` pour l'icône et le fichier `dll` :
            ```python
               a = Analysis(
                    ['main.py'],
                    pathex=[],
                    binaries=[],
                    datas=[('mlinzi_icon.ico', '.'),('libmysql.dll', '.'),('en.mo','mysql/connector/locales')],
                    hiddenimports=[],
                    hookspath=[],
                    hooksconfig={},
                    runtime_hooks=[],
                    excludes=[],
                    noarchive=False,
                )
        ```
       *   Supprimer la ligne `console=True` si elle existe dans `exe`.
       *   Modifier la ligne `name`.
   4.  **Exécuter la commande :**
      ```bash
       pyinstaller main.spec --onefile
      ```
  5. **Récupérer le fichier executable :**
      * Vous trouver le fichier `.exe` dans le dossier `dist`

## Utilisation

1.  **Lancez l'application** en exécutant `main.py` avec Python ou l'exécutable généré.
2.  **Configuration :**
    *   Renseignez le chemin vers `mysqldump.exe`.
    *   Entrez les informations de connexion à votre serveur MySQL (hôte, port, utilisateur, mot de passe).
    *   Cliquez sur "Connect" pour charger la liste des bases de données.
    *   Sélectionnez une base de données à sauvegarder.
    *   Choisissez un emplacement de destination pour les fichiers de sauvegarde.
3.  **Sauvegardes :**
    *   Activez ou désactivez les sauvegardes automatiques et configurez l'intervalle si nécessaire.
    *   Cliquez sur "Save Configuration" pour enregistrer vos paramètres et appliquer les changements.
    *   Cliquez sur "Start Backup" pour lancer une sauvegarde manuelle à tout moment.
4.  **Exportation :**
     *   Sélectionnez une sauvegarde dans la liste.
     *   Cliquez sur "Exporter la Sauvegarde" pour sélectionner un emplacement de destination.
5.  **Documentation**
    *    Cliquer sur le bouton `Help` pour avoir la documentation.
6.  **Autres options**
  *   Vous avez aussi une zone de logs pour suivre le déroulement des operations
  *  Une option est disponible pour démarrer l'application avec windows

## Structure du Projet
    mlinzi-auto-backup/
    ├── main.py # Script principal de l'application
    ├── mlinzi_icon.ico # Icône de l'application
    ├── libmysql.dll # Librairie nécessaire pour mysql
    ├── config.json # Fichier de configuration (si existant)
    └── requirements.txt # fichier pour les dépendances

    
## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez améliorer l'application, n'hésitez pas à :

1.  **Forker le dépôt.**
2.  **Créer une branche pour vos modifications (`git checkout -b ma-branche`).**
3.  **Faire vos changements et tester le tout**.
4.  **Faire un commit :** (`git commit -am 'Ajout de ma fonctionnalité'`).
5.  **Pousser vos changements:** (`git push origin ma-branche`).
6.  **Créer une `pull request`.**

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteur

**Willson Vulembere Antoine**

*   Email : willsonantoine@gmail.com
*   Téléphone : +243990084881
*   LinkedIn : [https://www.linkedin.com/in/cedryson-vulembere-368a76ba/](https://www.linkedin.com/in/cedryson-vulembere-368a76ba/)

## Soutien

Si ce projet vous est utile, n'hésitez pas à me soutenir en contribuant, en laissant une étoile sur le repository ou en faisant une petite donation.