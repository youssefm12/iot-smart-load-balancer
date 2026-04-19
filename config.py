# ─── Broker MQTT local ────────────────────────────────────────────────────────
MQTT_HOST = "localhost"
MQTT_PORT = 1883          # pas de TLS en local
MQTT_USER = ""
MQTT_PASS = ""

# ─── InfluxDB ─────────────────────────────────────────────────────────────────
INFLUX_URL    = "http://localhost:8086"
INFLUX_TOKEN  = ""        # on le récupère à l'étape suivante
INFLUX_ORG    = "iot-org"
INFLUX_BUCKET = "server-metrics"

# ─── Seuils load balancing ────────────────────────────────────────────────────
LOAD_THRESHOLD  = 80.0
TARGET_MAX_LOAD = 70.0
COOLDOWN_SEC    = 30

PUBLISH_INTERVAL = 5
