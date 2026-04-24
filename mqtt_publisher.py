"""
mqtt_publisher.py  —  Run this on your LAPTOP
Publishes random sensor data to the MQTT broker every 2 seconds.
 
Requirements:
    pip install paho-mqtt
 
Usage:
    python mqtt_publisher.py
"""
 
import json
import random
import ssl
import time
 
import paho.mqtt.client as mqtt
 
# ── Configuration ─────────────────────────────────────────────────────────────
BROKER_HOST = "set-p-gt-01-mqtt.bm.icts.kuleuven.be"
BROKER_PORT = 1883                    # TLS on port 1883 for this broker
CA_CERT     = "ca.crt"               # Path to the CA certificate
TOPIC       = "sensors/laptop/data"
CLIENT_ID   = "laptop-publisher"
 
# Client certificate auth — not required for this broker
CLIENT_CERT = None
CLIENT_KEY  = None
 
USERNAME    = "ee2-all"
PASSWORD    = "ee2-all"
# ─────────────────────────────────────────────────────────────────────────────
 
 
def on_connect(client, userdata, flags, rc):
    codes = {
        0: "Connected successfully",
        1: "Bad protocol version",
        2: "Client ID rejected",
        3: "Broker unavailable",
        4: "Bad username or password",
        5: "Not authorised",
    }
    print(f"[CONNECT] {codes.get(rc, f'Unknown code {rc}')}")
 
 
def on_publish(client, userdata, mid):
    print(f"[PUBLISH] Message {mid} delivered")
 
 
def configure_tls(client: mqtt.Client) -> None:
    client.tls_set(
        ca_certs=CA_CERT,
        certfile=CLIENT_CERT,
        keyfile=CLIENT_KEY,
        tls_version=ssl.PROTOCOL_TLS_CLIENT,
    )
 
 
def random_payload() -> dict:
    return {
        "timestamp":   time.time(),
        "temperature": round(random.uniform(18.0, 35.0), 2),   # °C
        "humidity":    round(random.uniform(30.0, 90.0), 2),   # %
        "pressure":    round(random.uniform(950.0, 1050.0), 2),  # hPa
        "value":       random.randint(0, 1023),
    }
 
 
def main():
    client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_publish = on_publish
 
    configure_tls(client)
 
    if USERNAME:
        client.username_pw_set(USERNAME, PASSWORD)
 
    print(f"Connecting to {BROKER_HOST}:{BROKER_PORT} …")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
 
    try:
        while True:
            payload = random_payload()
            result  = client.publish(TOPIC, json.dumps(payload), qos=1)
            print(f"[SEND] {payload}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping publisher…")
    finally:
        client.loop_stop()
        client.disconnect()
 
 
if __name__ == "__main__":
    main()
 