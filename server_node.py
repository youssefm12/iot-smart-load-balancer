import time, json, random, math, threading, os
import paho.mqtt.client as mqtt

SERVER_ID = int(os.environ.get("SERVER_ID", 1))
MQTT_HOST = os.environ.get("MQTT_HOST", "localhost")
MQTT_PORT = 1883
MQTT_USER = os.environ.get("MQTT_USER", "")
MQTT_PASS = os.environ.get("MQTT_PASS", "")
LOAD_THRESHOLD = 80.0
PUBLISH_INTERVAL = 5

class ServerNode:
    def __init__(self, server_id: int):
        self.sid        = server_id
        self.name       = f"server{server_id}"
        self.topic_base = f"servers/server{server_id}"
        self.topic_cmd  = "loadbalancer/commands"

        # Simulating base load
        self._base_cpu   = random.uniform(20, 50)
        self._base_ram   = random.uniform(30, 60)
        self._spike_at   = None
        self._overloaded = False
        self._lock       = threading.Lock()

        self.client = self._connect()

    def _connect(self):
        client = mqtt.Client(client_id=f"server-{self.sid}")
        if MQTT_USER and MQTT_PASS:
            client.username_pw_set(MQTT_USER, MQTT_PASS)
        client.on_connect = self._on_connect
        client.on_message = self._on_command
        # Attempt to connect infinitely because the broker might take a second to start
        while True:
            try:
                client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
                print(f"[{self.name}] Connecté au broker {MQTT_HOST}:{MQTT_PORT}")
                break
            except Exception as e:
                print(f"[{self.name}] Waiting for broker... {e}")
                time.sleep(2)
        client.loop_start()
        return client

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic_cmd, qos=1)

    def _on_command(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
            if data.get("target") == self.name and data.get("action") == "reduce_load":
                with self._lock:
                    self._overloaded = False
                    self._base_cpu   = max(20, self._base_cpu - 25)
                    self._base_ram   = max(20, self._base_ram - 20)
                print(f"[{self.name}] ✅ Charge réduite suite au load balancing")
        except Exception as e:
            pass

    def _generate_metrics(self):
        t = time.time()
        if self._spike_at is None:
            self._spike_at = t + random.uniform(60, 180)

        spike_factor = 0
        if t >= self._spike_at and not self._overloaded:
            spike_factor    = random.uniform(35, 55)
            self._overloaded = True
            self._spike_at   = t + random.uniform(60, 180)
        elif self._overloaded and t > self._spike_at + 60:
            self._overloaded = False

        noise_cpu = random.gauss(0, 3)
        noise_ram = random.gauss(0, 2)
        wave      = 10 * math.sin(t / 60)

        with self._lock:
            cpu = min(100, max(0, self._base_cpu + wave + noise_cpu + spike_factor))
            ram = min(100, max(0, self._base_ram + noise_ram + spike_factor * 0.6))

        network    = min(1000, random.uniform(50, 500) + spike_factor * 8)
        load_score = round(0.5 * cpu + 0.3 * ram + 0.2 * min(100, network / 10), 2)

        # Advanced Metrics Simulation
        # Temperature (Ambient ~25C + CPU Heat Factor)
        temp = 25 + (cpu * 0.55) + random.uniform(-1, 1)
        
        # Carbon Footprint (Roughly 1.5g CO2 per Load % per hour)
        co2 = (load_score * 1.5) + (network / 20) + random.uniform(0, 5)

        return {
            "timestamp": int(t),
            "cpu": round(cpu, 2),
            "ram": round(ram, 2),
            "network": round(network, 2),
            "load_score": load_score,
            "temp": round(temp, 2),
            "co2": round(co2, 2)
        }

    def run(self):
        print(f"[{self.name}] Publication toutes les {PUBLISH_INTERVAL}s")
        while True:
            metrics = self._generate_metrics()
            
            # Publish individual metrics according to Report Section 3.4
            self.client.publish(f"{self.topic_base}/cpu", str(metrics['cpu']), qos=1)
            self.client.publish(f"{self.topic_base}/ram", str(metrics['ram']), qos=1)
            self.client.publish(f"{self.topic_base}/network", str(metrics['network']), qos=1)
            self.client.publish(f"{self.topic_base}/load", str(metrics['load_score']), qos=1)
            self.client.publish(f"{self.topic_base}/temp", str(metrics['temp']), qos=1)
            self.client.publish(f"{self.topic_base}/co2", str(metrics['co2']), qos=1)
            
            # Consolidated payload for easy Node-RED parsing
            metrics["server_id"] = self.name
            self.client.publish(f"{self.topic_base}/metrics", json.dumps(metrics), qos=1)
            
            status = "🔴 SURCHARGE" if metrics["load_score"] > LOAD_THRESHOLD else "🟢 OK"
            colors = "\033[96m" if "OK" in status else "\033[91m"
            reset = "\033[0m"
            print(f"[{colors}{self.name}{reset}] CPU={metrics['cpu']:>4.1f}% | Temp={metrics['temp']:>4.1f}°C | CO2={metrics['co2']:>5.1f}g/h | {status}")
            
            time.sleep(PUBLISH_INTERVAL)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    node = ServerNode(SERVER_ID)
    try:
        node.run()
    except KeyboardInterrupt:
        node.disconnect()
