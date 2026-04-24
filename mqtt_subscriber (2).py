"""
mqtt_subscriber.py  —  Run this on your RASPBERRY PI
Subscribes to the topic and prints incoming data.

Requirements:
    pip install paho-mqtt

Usage:
    python mqtt_subscriber.py
"""

import json
import ssl

import paho.mqtt.client as mqtt

# ── Configuration ─────────────────────────────────────────────────────────────
BROKER_HOST = "set-p-gt-01-mqtt.bm.icts.kuleuven.be"
BROKER_PORT = 1883
CA_CERT     = "ca.crt"               # copy ca.crt to the Pi as well
TOPIC       = "sensors/laptop/data"
CLIENT_ID   = "rpi-subscriber"

# Client certificate auth — not required for this broker
CLIENT_CERT = None
CLIENT_KEY  = None

USERNAME    = "ee2-all"
PASSWORD    = "ee2-all"
# ─────────────────────────────────────────────────────────────────────────────


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[CONNECT] Connected — subscribing to '{TOPIC}'")
        client.subscribe(TOPIC, qos=1)
    else:
        print(f"[CONNECT] Failed with code {rc}")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(
            f"[RECV] topic={msg.topic} | "
            f"temp={data.get('temperature')}°C  "
            f"humidity={data.get('humidity')}%  "
            f"pressure={data.get('pressure')} hPa  "
            f"value={data.get('value')}"
        )
    except json.JSONDecodeError:
        print(f"[RECV] Raw: {msg.payload}")


def on_disconnect(client, userdata, rc):
    print(f"[DISCONNECT] rc={rc}")


def configure_tls(client: mqtt.Client) -> None:
    client.tls_set(
        ca_certs=CA_CERT,
        certfile=CLIENT_CERT,
        keyfile=CLIENT_KEY,
        tls_version=ssl.PROTOCOL_TLS_CLIENT,
    )


def main():
    client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv5)
    client.on_connect    = on_connect
    client.on_message    = on_message
    client.on_disconnect = on_disconnect

    configure_tls(client)

    if USERNAME:
        client.username_pw_set(USERNAME, PASSWORD)

    print(f"Connecting to {BROKER_HOST}:{BROKER_PORT} …")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()   # blocks; Ctrl-C to stop


if __name__ == "__main__":
    main()
