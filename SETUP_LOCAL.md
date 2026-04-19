# 🚀 Configuration Locale — Architecture IoT Sans AWS

## 🟡 Étape 1 — Installer les 4 outils (Windows)

Ouvre **PowerShell EN ADMINISTRATEUR** et exécute ces commandes :

```powershell
# 1. Mosquitto (broker MQTT)
winget install EclipseFoundation.Mosquitto

# 2. Node-RED (moteur de règles + intégration InfluxDB)
npm install -g --unsafe-perm node-red

# 3. InfluxDB (base de données time-series)
winget install InfluxData.InfluxDB

# 4. Grafana (dashboard)
winget install GrafanaLabs.Grafana
```

> **⚠️ Si `winget` ne fonctionne pas pour Mosquitto :**
> - Télécharge l'installeur : https://mosquitto.org/download/
> - Choisis **Windows x64**

---

## 🟡 Étape 2 — Démarrer les services

Ouvre **4 terminaux PowerShell séparés** (pas en admin, sauf Grafana) et lance :

```powershell
# Terminal 1 — Mosquitto (broker MQTT)
mosquitto -v

# Terminal 2 — Node-RED
node-red

# Terminal 3 — InfluxDB
influxd

# Terminal 4 — Grafana
& "C:\Program Files\GrafanaLabs\grafana\bin\grafana-server.exe"
```

Attends quelques secondes que chaque service démarre. Tu devrais voir :
- **Mosquitto** : `mosquitto version X.X.X`
- **Node-RED** : `Welcome to Node-RED` + port 1880
- **InfluxDB** : `Listening on HTTP` port 8086
- **Grafana** : `HTTP Server Listen` port 3000

---

## 🟡 Étape 3 — Installer les dépendances Python

Dans ton terminal principal (dans `iot-server-monitor`) :

```powershell
cd d:\iot-server-monitor
pip install -r requirements.txt
```

---

## 🟡 Étape 4 — Configurer InfluxDB (Interface Web)

1. Ouvre **http://localhost:8086** dans ton navigateur
2. Clique sur **Get Started**
3. Remplis les informations :
   - **Username** : `admin`
   - **Password** : `admin1234`
   - **Organization** : `iot-org`
   - **Bucket** : `server-metrics`
4. Clique **Continue**
5. **Copie le token généré** → tu vas l'utiliser dans le Flow Node-RED

---

## 🟡 Étape 5a — Installe d'abord le node InfluxDB dans Node-RED

1. Ouvre **http://localhost:1880** dans ton navigateur
2. Menu ☰ (haut-gauche) → **Manage palette**
3. Onglet **Install** (2e onglet)
4. Cherche : `node-red-contrib-influxdb`
5. Clique le bouton **Install**
6. Attends ~30 sec que l'installation se termine

---

## 🟡 Étape 5b — Crée la connexion InfluxDB

1. **Toujours dans Node-RED**, Menu ☰ → **Settings** → Onglet **Nodes**
2. Cherche `node-red-contrib-influxdb` → Clique sur **Configure**
3. Remplis :
   - **URL** : `http://localhost:8086`
   - **Organization** : `iot-org`
   - **Bucket** : `server-metrics`
   - **Token** : *colle ton token ici* :
   ```
   g2PJf1c8jB2E6a8njis1ZA3NvpPvxph13ineFbWr0xlvTwDpuZpTdZURThQQ6010renBOpp7RoEzoAsMcCIWxA ==
   ```
4. Clique **Done**

---

## 🟡 Étape 5c — Importe le flow Node-RED

1. Menu ☰ → **Import** → colle ce JSON :

```json
[
  {"id":"mqtt-broker","type":"mqtt-broker","name":"Local Mosquitto","broker":"localhost","port":"1883","clientid":"","usetls":false,"compatmode":true,"protocolVersion":"4","keepalive":"60","cleansession":true,"birthTopic":"","birthQos":"0","birthPayload":"","closeTopic":"","closeQos":"0","closePayload":"","willTopic":"","willQos":"0","willPayload":""},
  
  {"id":"mqtt-in","type":"mqtt in","z":"","name":"","topic":"servers/+/metrics","qos":"1","datatype":"json","broker":"mqtt-broker","nl":false,"rap":true,"rh":0,"wires":[["parse"]]},
  
  {"id":"parse","type":"json","z":"","name":"Parse JSON","property":"payload","action":"","pretty":false,"wires":[["lb-rule","debug-metrics"]]},
  
  {"id":"debug-metrics","type":"debug","z":"","name":"📊 Metrics","active":true,"tosidebar":true,"console":false,"tostatus":false,"complete":"payload","targetType":"msg","statusVal":"","statusType":"auto","wires":[]},
  
  {"id":"lb-rule","type":"function","z":"","name":"⚡ Load Balancing Logic","func":"const d = msg.payload;\n\nif (d.load_score <= 80) {\n  return null;  // pas de surcharge\n}\n\nconst now = Date.now();\nglobal.states = global.states || {};\nglobal.lastAction = global.lastAction || {};\nglobal.states[d.server_id] = d.load_score;\n\n// Vérifier cooldown\nif ((now - (global.lastAction[d.server_id] || 0)) < 30000) {\n  return null;\n}\n\n// Trouver le serveur le moins chargé\nconst others = Object.entries(global.states)\n  .filter(([k, v]) => k !== d.server_id && v < 70)\n  .sort((a, b) => a[1] - b[1]);\n\nif (!others.length) {\n  return null;  // Aucune cible\n}\n\nglobal.lastAction[d.server_id] = now;\nmsg.payload = {\n  action: 'reduce_load',\n  source: d.server_id,\n  target: others[0][0],\n  load_score: d.load_score,\n  timestamp: Math.floor(now / 1000)\n};\nreturn msg;","outputs":1,"noerr":0,"initialize":"","finalize":"","libs":[],"wires":[["mqtt-cmd","mqtt-alert","debug-lb"]]},
  
  {"id":"debug-lb","type":"debug","z":"","name":"⚡ LB Actions","active":true,"tosidebar":true,"console":false,"tostatus":false,"complete":"payload","targetType":"msg","statusVal":"","statusType":"auto","wires":[]},
  
  {"id":"mqtt-cmd","type":"mqtt out","z":"","name":"→ Publish Command","topic":"loadbalancer/commands","qos":"1","retain":"false","broker":"mqtt-broker","wires":[]},
  
  {"id":"mqtt-alert","type":"mqtt out","z":"","name":"→ Publish Alert","topic":"loadbalancer/alerts","qos":"1","retain":"false","broker":"mqtt-broker","wires":[]},
  
  {"id":"influx-format","type":"function","z":"","name":"Format InfluxDB","func":"const d = msg.payload;\nmsg.payload = [{\n  measurement: 'server_metrics',\n  tags: {\n    server_id: d.server_id\n  },\n  fields: {\n    cpu: d.cpu,\n    ram: d.ram,\n    network_mbps: d.network_mbps,\n    load_score: d.load_score\n  },\n  timestamp: d.timestamp * 1e9\n}];\nreturn msg;","outputs":1,"noerr":0,"initialize":"","finalize":"","libs":[],"wires":[["influx-write"]]},
  
  {"id":"influx-write","type":"influxdb out","z":"","name":"📊 Write to InfluxDB","measurement":"server_metrics","precision":"ns","influxdb":"influx-conn","wires":[]}
]
```

2. Clique **Import**
3. **Deploy** (bouton rouge en haut-droit)

---

## ✅ Teste la connexion

Si tu vois les données passer dans **Node-RED** (onglet **Debug** à droite) et qu'il y a **0 erreurs** : c'est bon ! 🎉

---

## 🟡 Étape 6 — Installer les dépendances Python

```powershell
cd d:\iot-server-monitor
pip install -r requirements.txt
```

---

## ▶️ Lancer L'APPLICATION

Dans PowerShell, dans le dossier `iot-server-monitor` :

```powershell
python run_all.py
```

Tu devrais voir :

```
============================================================
  IoT Server Monitor — Load Balancing System   
============================================================
[LoadBalancer] Connecté au broker local (rc=0)
[LoadBalancer] En écoute sur servers/+/metrics ...
[server1] Connecté au broker local (rc=0)
[server2] Connecté au broker local (rc=0)
[server3] Connecté au broker local (rc=0)
[server4] Connecté au broker local (rc=0)
[server1] Publication toutes les 5s
[server1] CPU=45.2% RAM=38.1% Load=42.3 🟢 OK
...
[LoadBalancer] ⚡ Migration server3 → server2 (load=78.6%)
```

---

## ✅ Vérification

| URL | Ce que tu dois voir |
|-----|---|
| http://localhost:1880 | Node-RED — Flow avec messages qui passent en temps réel |
| http://localhost:8086 | InfluxDB — Données dans bucket `server-metrics` |
| http://localhost:3000 | Grafana (login `admin` / `admin`) — prêt à créer des dashboards |

---

## 🔜 Prochaine étape

Une fois que `run_all.py` tourne et que tu vois les messages passer dans Node-RED, dis-moi !  
On va créer le **dashboard Grafana** avec graphiques temps réel 📊
