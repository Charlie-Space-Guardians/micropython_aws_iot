#################
#  WiFi Setup	#
#################
import json

import secrets
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("Connecting to WiFi Network...")
wlan.connect(secrets.WIFI_SSID,secrets.WIFI_PASSWORD)
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
MQTT_ENVIROMENTAL_TOPIC = "picow/envirosensor"


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
    msg_str_dict = {"temperature": temperature,"pressure": pressure,"humidity": humidity,"gas": gas}

    msg_str = json.dumps(msg_str_dict)
    print(f"TX: {topic_str}\n\t{msg_str}")
    mqtt_client.publish(topic_str, msg_str)
    


# callback function to periodically send MQTT ping messages
# to the MQTT broker
def send_mqtt_ping():
    print("TX: ping")
    mqtt_client.ping()

led = Pin("LED", Pin.OUT)

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
#button.irq(publish_mqtt_button_msg, Pin.IRQ_FALLING | Pin.IRQ_RISING)

# turn on-board LED on
led.on()

# create timer for periodic MQTT ping messages for keep-alive
mqtt_ping_timer = Timer(
    mode=Timer.PERIODIC, period=mqtt_client.keepalive * 1000, callback=send_mqtt_ping
)

#############################
#  Sensor+Display Setup 	#
#############################
import time
import machine
import utime
import _thread
from gfx_pack import GfxPack
from breakout_bme68x import BreakoutBME68X, STATUS_HEATER_STABLE

# Settings
lower_temp_bound = 30
upper_temp_bound = 40
use_bme68x_breakout = True

sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)  # used for calculating a temperature from the raw sensor reading

gp = GfxPack()
gp.set_backlight(4, 0, 0)  # turn the RGB backlight off
display = gp.display
display.set_backlight(0.2)  # set the white to a low value

if use_bme68x_breakout:
    bmp = BreakoutBME68X(gp.i2c)

display.set_pen(0)
display.clear()
display.set_font("bitmap14_outline")

while True:
    # Clear display
    display.set_pen(0)
    display.clear()

    display.set_pen(15)
    #display.text("GFXPack Temp demo", 0, 0, scale=0.1)

    if use_bme68x_breakout:
        temperature, pressure, humidity, gas, status, _, _ = bmp.read()
        display.text("Gas: {:0.2f}kOhms".format(gas/1000), 0, 0, scale=0.2)
        display.text("Temp: {:0.2f}c".format(temperature), 0, 20, scale=0.2)
        display.text("Press: {:0.2f}hPa".format(pressure/100), 0, 35, scale=0.2)
        display.text("Humid: {:0.2f}%".format(humidity), 0, 50, scale=0.2)

        heater = "Stable" if status & STATUS_HEATER_STABLE else "Unstable"
        print("{:0.2f}c, {:0.2f}Pa, {:0.2f}%, {:0.2f} Ohms, Heater: {}".format(
            temperature, pressure, humidity, gas, heater))

    else:
        reading = sensor_temp.read_u16() * conversion_factor
        temperature = 27 - (reading - 0.706) / 0.001721
        display.text("Temperature", 25, 15, scale=0.2)
        display.text("{:0.2f}c".format(temperature), 25, 30, scale=2)

    if temperature < lower_temp_bound:
        r = 255
        b = 0
    elif temperature > upper_temp_bound:
        r = 255
        b = 0
    else:
        r = (temperature - lower_temp_bound) / (upper_temp_bound - lower_temp_bound) * 255
        b = 255 - ((temperature - lower_temp_bound) / (upper_temp_bound - lower_temp_bound) * 255)

    gp.set_backlight(r, 75, b)
    display.update()
    publish_mqtt_button_msg()
    mqtt_client.check_msg()
    
    time.sleep(10)
    
     