#!/usr/bin/python
# 2022 Andrew Villeneuve

# Listen and respond to relay control events via MQTT

# 2022/02 Wiring
# R1: Unused (Not working)
# R2: Unused
# R3: APi
# R4: Unused

## MQTT Config
mqtt_broker = "mqtt"
mqtt_port = 1883
mqtt_topic_base = "network_control/lab/bounce/"
mqtt_client_id = "baba_relay_server"
mqtt_device = [
    { 'topic': mqtt_topic_base + "relay01", 'unique_id': 'lab_relay_01', 'friendly': 'Lab Relay 01' },
    { 'topic': mqtt_topic_base + "relay02", 'unique_id': 'lab_relay_02', 'friendly': 'Lab Relay 02' },
    { 'topic': mqtt_topic_base + "relay03", 'unique_id': 'lab_relay_03', 'friendly': 'Lab Relay 03' },
    { 'topic': mqtt_topic_base + "relay04", 'unique_id': 'lab_relay_04', 'friendly': 'Lab Relay 04' }
]

## Home Assistant Auto-Discovery Config
mqtt_discovery_topic = "homeassistant/button/%s/config"
mqtt_discovery_payload = '{"device_class": "restart", "name": "%s", "unique_id": "%s", "command_topic": "%s" }'
ha_discovery = True

## Imports 
import sys
import signal
from time import sleep
from gpiozero import LED
import paho.mqtt.client as mqtt

## Implementation
print("relay_server starting up...")

## Init GPIOs
relay01 = LED(17, active_high=False, initial_value=False)
relay02 = LED(27, active_high=False, initial_value=False)
relay03 = LED(22, active_high=False, initial_value=False)
relay04 = LED(26, active_high=False, initial_value=False)

## Define Subs
def bounce(relay):
    relay.on()
    sleep(2)
    relay.off()

def on_connect(client, userdata, flags, rc):
    print("Connected to broker")
    client.subscribe(mqtt_topic_base + "#")

def on_message(client, userdata, message):
    print("Got Message: %s %s" % (message.topic, message.payload))
    if message.topic == mqtt_device[0]['topic']:
        print("Bouncing relay 1")
        bounce(relay01)
    elif message.topic == mqtt_device[1]['topic']:
        print("Bouncing relay 2")
        bounce(relay02)
    elif message.topic == mqtt_device[2]['topic']:
        print("Bouncing relay 3")
        bounce(relay03)
    elif message.topic == mqtt_device[3]['topic']:
        print("Bouncing relay 4")
        bounce(relay04)
    else:
        print("Error: unrecognized bounce target topic: %s" % (message.topic))

# Advertise HA discovery topic
def mqtt_announce(client):
    for i in mqtt_device:
        dt = mqtt_discovery_topic % (i['unique_id'])
        dp = mqtt_discovery_payload % (i['friendly'], i['unique_id'], i['topic'])
        print("Sending discovery advertisment for %s : %s" % (dt, dp))
        client.publish(dt, dp)

def mqtt_unannounce():
    global client
    for i in mqtt_device:
        dt = mqtt_discovery_topic % (i['unique_id'])
        dp = "{}"
        print("Sending discovery retraction for %s : %s" % (dt, dp))
        client.publish(dt, dp)

def cleanup(sig, frame):
    print("Caught interrupt, cleaning up")
    if ha_discovery:
        mqtt_unannounce()
    client.loop_stop()
    sys.exit(0)

# Instantiate a client and register callbacks
client = mqtt.Client(mqtt_client_id)
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port)
client.loop_start()

# Register SIGINT handler
signal.signal(signal.SIGINT, cleanup)

print("relay_server entering event loop")
while True:
    # Send auto-configuration topic to Home Assistant
    if ha_discovery:
        mqtt_announce(client)
    sleep(300)

