#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║               🐵 CHAOS MONKEY — IoT Attack Simulator        ║
╚══════════════════════════════════════════════════════════════╝
"""

import time, json, random, math, argparse, sys
import paho.mqtt.client as mqtt

# Force UTF-8 for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# ─── ANSI Colors ───
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

BANNER = f"{RED}{BOLD}[ CHAOS MONKEY - IoT ATTACK SIMULATOR ]{RESET}"

PHASES = [
    {"name": "🔍 RECON",        "duration": 5,  "cpu_range": (30, 45),  "ram_range": (25, 40),  "net_range": (100, 200)},
    {"name": "⚡ ESCALATION",   "duration": 8,  "cpu_range": (50, 70),  "ram_range": (40, 60),  "net_range": (300, 500)},
    {"name": "🔥 FULL ATTACK",  "duration": 12, "cpu_range": (85, 99),  "ram_range": (75, 95),  "net_range": (700, 999)},
    {"name": "💀 CRITICAL",     "duration": 10, "cpu_range": (95, 100), "ram_range": (90, 100), "net_range": (900, 1000)},
    {"name": "📉 COOLDOWN",     "duration": 8,  "cpu_range": (60, 30),  "ram_range": (50, 25),  "net_range": (400, 100)},
    {"name": "🟢 RECOVERY",     "duration": 5,  "cpu_range": (20, 35),  "ram_range": (20, 35),  "net_range": (50, 150)},
]

def progress_bar(value, max_val=100, width=20):
    filled = int(width * value / max_val)
    color = RED if value >= 80 else YELLOW if value >= 60 else GREEN
    return f"[{color}{'#' * filled}{DIM}{'-' * (width - filled)}{RESET}] {color}{value:5.1f}%{RESET}"

def run_attack(target_server, mqtt_host, mqtt_port, mqtt_user, mqtt_pass):
    print(BANNER)
    print(f"Target: {target_server} | Host: {mqtt_host}")
    
    client = mqtt.Client(client_id=f"monkey-{random.randint(1000,9999)}")
    if mqtt_user and mqtt_pass: client.username_pw_set(mqtt_user, mqtt_pass)
    
    try:
        client.connect(mqtt_host, mqtt_port)
        client.loop_start()
    except Exception as e:
        print(f"Error: {e}")
        return

    topic = f"servers/{target_server}/metrics"
    for phase in PHASES:
        print(f"\nPhase: {phase['name']}")
        for _ in range(phase['duration']):
            cpu = random.uniform(*phase['cpu_range'])
            ram = random.uniform(*phase['ram_range'])
            net = random.uniform(*phase['net_range'])
            load = round(0.5*cpu + 0.3*ram + 0.2*min(100, net/10), 2)
            
            payload = {
                "server_id": target_server, "cpu": round(cpu,2), "ram": round(ram,2),
                "network": round(net,2), "load_score": load, 
                "temp": round(25 + cpu*0.55, 2), "co2": round(load*1.5, 2),
                "timestamp": int(time.time())
            }
            client.publish(topic, json.dumps(payload))
            sys.stdout.write(f"\rLoad: {progress_bar(load)}")
            sys.stdout.flush()
            time.sleep(1)
    client.loop_stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", default="server2")
    parser.add_argument("--host", default="localhost")
    args = parser.parse_args()
    run_attack(args.target, args.host, 1883, "iot_admin", "iot_secure_123")
