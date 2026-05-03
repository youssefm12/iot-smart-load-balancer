# 📘 Annexe Technique : IoT Smart Load Balancer

## 1. Introduction
Ce projet implémente un système intelligent d'équilibrage de charge pour un cluster de serveurs IoT. Le système surveille en temps réel les ressources (CPU, RAM, Réseau) et intervient automatiquement pour redistribuer la charge lorsqu'un seuil critique est atteint.

---

## 2. Architecture du Système

Le projet repose sur une pile technologique moderne orchestrée par Docker :
- **MQTT (Mosquitto)** : Protocole de communication léger pour l'IoT.
- **Node-RED** : Moteur de règles et d'analyse de données.
- **InfluxDB 2.7** : Base de données de séries temporelles pour le stockage des métriques.
- **Grafana** : Interface de visualisation et de monitoring.
- **Python (Paho-MQTT)** : Langage utilisé pour simuler les serveurs (nœuds).

### Schéma des flux de données
1. Les **nœuds Python** publient leurs métriques sur `servers/+/metrics`.
2. **Node-RED** traite ces données, les stocke dans **InfluxDB** et analyse les seuils.
3. Si une surcharge est détectée (> 80%), Node-RED publie une commande sur `loadbalancer/commands`.
4. Le nœud concerné reçoit la commande et réduit sa charge instantanément.

---

## 3. Explication du Code Source

### 3.1 Simulation des Serveurs (`server_node.py`)
Le script simule un serveur réel avec des variations de charge.
- **Metrics** : Génère CPU, RAM, Network, Température et CO2.
- **Réduction de charge** : La méthode `_on_command` intercepte les ordres du Load Balancer pour simuler une migration réussie.
- **Green IT** : Le calcul de l'empreinte carbone (CO2) est intégré pour sensibiliser à l'aspect écologique des centres de données.

### 3.2 Intelligence Artificielle / Logique (`Node-RED`)
Le flux Node-RED contient un nœud "Function" nommé **⚡ Load Balancing Logic**.
- **Algorithme** :
    ```javascript
    if (load_score > 80) {
        // Recherche du serveur le moins chargé
        // Envoi de l'ordre de migration
    }
    ```
- **Cooldown** : Un délai de 30 secondes évite que le système ne réagisse trop nerveusement à des pics de charge très courts.

### 3.3 Système d'Alerting (Telegram)
Pour assurer une réactivité maximale, le système intègre un **Bot Telegram** :
- **Rôle** : Notifier l'administrateur en temps réel lors d'une surcharge.
- **Détails** : Le message inclut l'état du cluster, la charge moyenne et l'action corrective entreprise. Cela permet un monitoring mobile sans avoir besoin d'être devant Grafana.

---

## 4. Procédure pour Reproduire le Projet

### Prérequis
- Docker Desktop installé et fonctionnel.
- Python 3.9+ (pour exécuter le Chaos Monkey en local).

### Étapes de déploiement
1. **Extraction** : Décompressez le projet dans un dossier.
2. **Lancement de l'infrastructure** :
   ```bash
   docker-compose up -d --build
   ```
3. **Accès aux services** :
   - **Grafana** : `http://localhost:3000` (User: `admin` | Pass: `admin`)
   - **Node-RED** : `http://localhost:1880`
   - **InfluxDB** : `http://localhost:8086`

### Import du Dashboard Grafana
Le dashboard est normalement importé automatiquement. Si ce n'est pas le cas :
- Allez dans **Dashboards > Import**.
- Chargez le fichier `docker/grafana/dashboards/main_dashboard.json`.

---

## 5. Guide de Démonstration (Soutenance)

Pour prouver que le système fonctionne pendant votre présentation :
1. Ouvrez votre terminal.
2. Activez l'environnement virtuel : `.\venv\Scripts\Activate.ps1`.
3. Lancez une attaque sur le serveur 3 :
   ```bash
   python chaos_monkey.py server3
   ```
4. **Observez Grafana** : La courbe du serveur 3 va monter en flèche, puis redescendre dès que Node-RED aura envoyé la commande de correction.

---

## 6. Annexe : Configuration des Alertes Telegram (Optionnel)

Pour recevoir les alertes sur votre propre téléphone pendant vos tests, suivez ces étapes simples :

### A. Activation du Bot existant
1. Recherchez le bot **`@IotServerMonitorBot`** sur Telegram.
2. Cliquez sur **Démarrer** (`/start`).

### B. Liaison avec votre compte
Pour que le système sache à qui envoyer les alertes :
1. Recherchez le bot **`@userinfobot`** sur Telegram et envoyez-lui un message.
2. Notez l'**ID** qu'il vous renvoie (ex: `123456789`).

### C. Mise à jour dans le code source
1. Ouvrez l'interface Node-RED (`http://localhost:1880`).
2. Double-cliquez sur le nœud **"📨 Format Telegram Alert"**.
3. Dans l'onglet "Function", remplacez la valeur numérique de `chat_id` par votre propre ID.
4. Cliquez sur **Deploy** (bouton rouge en haut à droite).

*Désormais, lors de la prochaine surcharge simulée avec le Chaos Monkey, vous recevrez l'alerte directement sur votre compte Telegram via le bot du projet.*

---
*Ce document fait partie intégrante des livrables pour le projet Technologies IoT 2026.*
