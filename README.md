# Projet de Monitoring avec API en Python
Ce projet est une application de monitoring équipée d'une API en Python permettant de surveiller diverses métriques système.

## Instructions de démarrage
1. Cloner le dépôt :
```bash
git clone https://github.com/votre_utilisateur/votre_projet.git
```
2. Lancer les conteneurs Docker :
```bash
docker-compose up
```
3. Démarrer l'API :
```bash
python3 main.py
```
L'API sera désormais accessible à l'adresse http://127.0.0.1:3000.

## Utilisation de l'API
Vous pouvez explorer et tester les différentes fonctionnalités de l'API en utilisant Swagger. Accédez à http://127.0.0.1:3000 dans votre navigateur pour accéder à l'interface Swagger.

## Configuration
Le fichier de configuration de l'application est situé à l'emplacement suivant :

```bash
/etc/monit/monit_config.json
```
Vous pouvez ajuster les paramètres de configuration selon vos besoins dans ce fichier.
