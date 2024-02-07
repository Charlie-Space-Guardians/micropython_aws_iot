#################
#  WiFi Setup	#
#################
import json

import secrets
import network
import binascii
import ubinascii

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()

## Scan Network
print("Scanning WiFi Network...")
networks = wlan.scan()  # list with tupples with 6 fields ssid, bssid, channel, RSSI, security, hidden
i = 0
networks.sort(key=lambda x: x[3], reverse=True)  # sorted on RSSI (3)
for w in networks:
    i += 1
    print(i, w[0].decode(), binascii.hexlify(w[1]).decode(), w[2], w[3], w[4], w[5])

print("Connecting to WiFi Network...")
wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
while not wlan.isconnected():
    pass

print(wlan.isconnected())
print(wlan.ifconfig())
#############################
#  AWS  			Setup	#
#############################
import machine
import network
import ssl
import time
import ubinascii

from machine import Pin, Timer

import ntptime

from umqtt.simple import MQTTClient

# MQTT client and broker constants
MQTT_CLIENT_KEY = "private.pem.key"
MQTT_CLIENT_CERT = "certificate.pem.crt"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())

MQTT_BROKER = secrets.MQTT_BROKER
MQTT_BROKER_CA = "AmazonRootCA1.pem"

# MQTT topic constants
MQTT_LED_TOPIC = "picow/led"
MQTT_ENVIROMENTAL_TOPIC = "device/88/data"


# function that reads PEM file and return byte array of data
def read_pem(file):
    with open(file, "r") as input:
        text = input.read().strip()
        split_text = text.split("\n")
        base64_text = "".join(split_text[1:-1])

        return ubinascii.a2b_base64(base64_text)


# callback function to handle received MQTT messages
def on_mqtt_msg(topic, msg):
    # convert topic and message from bytes to string
    topic_str = topic.decode()
    msg_str = msg.decode()

    print(f"RX: {topic_str}\n\t{msg_str}")

    # process message
    if topic_str is MQTT_LED_TOPIC:
        if msg_str is "on":
            led.on()
        elif msg_str is "off":
            led.off()
        elif msg_str is "toggle":
            led.toggle()


# callback function to handle changes in button state
# publishes "released" or "pressed" message
def publish_mqtt_button_msg():
    topic_str = MQTT_ENVIROMENTAL_TOPIC

    msg_str_dict = {"time_unix": int(time.time()), "mac_address": mac, "proximity": proximity,
                    "ambient_lux": ambient_lux}

    msg_str = json.dumps(msg_str_dict)
    print(f"TX: {topic_str}\n\t{msg_str}")
    mqtt_client.publish(topic_str, msg_str)


# callback function to periodically send MQTT ping messages
# to the MQTT broker
def send_mqtt_ping():
    print("TX: ping")
    mqtt_client.ping()


# read the data in the private key, public certificate, and
# root CA files
key = read_pem(MQTT_CLIENT_KEY)
cert = read_pem(MQTT_CLIENT_CERT)
ca = read_pem(MQTT_BROKER_CA)

# create MQTT client that use TLS/SSL for a secure connection
mqtt_client = MQTTClient(
    MQTT_CLIENT_ID,
    MQTT_BROKER,
    keepalive=60,
    ssl=True,
    ssl_params={
        "key": key,
        "cert": cert,
        "server_hostname": MQTT_BROKER,
        "cert_reqs": ssl.CERT_REQUIRED,
        "cadata": ca,
    },
)

# update the current time on the board using NTP
ntptime.settime()

print(f"Connecting to MQTT broker: {MQTT_BROKER}")

# register callback to for MQTT messages, connect to broker and
# subscribe to LED topic
mqtt_client.set_callback(on_mqtt_msg)
mqtt_client.connect()
mqtt_client.subscribe(MQTT_LED_TOPIC)

print(f"Connected to MQTT broker: {MQTT_BROKER}")

# register callback function to handle changes in button state
# button.irq(publish_mqtt_button_msg, Pin.IRQ_FALLING | Pin.IRQ_RISING)

# create timer for periodic MQTT ping messages for keep-alive
mqtt_ping_timer = Timer(1,
                        mode=Timer.PERIODIC, period=mqtt_client.keepalive * 1000, callback=send_mqtt_ping
                        )

#############################
#  Sensor+Display Setup 	#
#############################
import time
import machine
import utime
import time
from machine import Pin, I2C
import vcnl4020

i2c = I2C(sda=Pin(21), scl=Pin(22))  # Correct I2C pins for RP2040
vcn = vcnl4020.VCNL4020(i2c)
vcn.proximity_rate = vcnl4020.SAMPLERATE_250

while True:
    proximity = vcn.proximity
    ambient_lux = vcn.ambient
    print(f"Proximity: {proximity}")
    print(f"Ambient light: {ambient_lux} lux")
    print()
    time.sleep(1.0)

    publish_mqtt_button_msg()
    mqtt_client.check_msg()

    time.sleep(50)




