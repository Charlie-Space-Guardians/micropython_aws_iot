
# Readme.md

## Introduction

This is a repository for the University of Aberdeen CS3528 Group project.
This is an Internet of Things (IoT) and MicroPython based implementation of sensing solution
for the purpose of monitoring the variables from the sensors and sending the data to the cloud,
using Message Queuing Telemetry Transport (MQTT) protocol.

**This branch is for the Pico-W environmental sensor.**

## Prerequisites

The following prerequisites from your MQTT provider are required before flashing and modifying the code:
 - MQTT Broker Address
 - MQTT Broker Certificate
 - MQTT Client Key
 - MQTT Client Certificate
 - Authorized Internet Connection

## Micropython Guide

### Preamble

Conventional way is to use [Thonny IDE](https://github.com/thonny/thonny) to flash the code to the Pico-W,
as it provides a user-friendly interface and a built-in serial monitor.
Also be sure to connect your chosen sensors to your Pico-W to their regarding communication protocol
(eg. I2C, SPI, UART, etc.). This following branch has it's own sensor implemented in the code,
with the following sensors:
 - BME688 (Volatile Organic Compound (VOC), Temperature, Humidity, Pressure)
 - SCD41 (Carbon Dioxide (CO2), Temperature, Humidity)

#### Flashing the firmware

You may or not have to also flash your Pico-W with the latest MicroPython firmware, which there are two supported
flavours:
 - [MicroPython](https://micropython.org/download/RPI_PICO_W/)
 - [Pimoroni MicroPython](https://github.com/pimoroni/pimoroni-pico)

To flash, before connecting the Pico-W to your computer, hold the BOOTSEL button and
connect the Pico-W to your computer. Copy the .uf2 firmware file to the RPI-RP2 drive that appears
on your system drive. The Pico-W will automatically reboot and the firmware will be flashed.

#### Connecting to the Pico-W

After flashing the firmware, you can connect to the Pico-W using the Thonny IDE. 
To setup, on the menu bar, click on `Run` and then `Select Interpreter`.
Select the `MicroPython (Raspberry Pi Pico)` option and click `OK`.
You may need to select the serial port that the Pico-W is connected to manually,
if it doesn't automatically connect!
Now you should be able to see in your Thonny IDE the REPL (Read-Eval-Print Loop) prompt,
where you can run your MicroPython code in the shell, if it is still hanging you may need
stop the current running code by clicking the stop button on the menu bar.

To upload files to the Pico-W, you can use the `Files` tab on the left-hand side of the Thonny IDE.
You can drag and drop files to the Pico-W, and you can also create new files and folders or the
left-click on the file to upload it to either the Pico-W or the local system.

## AWS Guide

To connect to the AWS IoT Core, you will need to create a "thing" with a certificate and a policy.

### Policy Creation

1. Go to the AWS IoT Core console.
2. Click on "Secure" on the left-hand side.
3. Click on "Policies".
4. Click on "Create a policy".
5. Enter a name for the policy.
6. In the "Action" section, click on "Add statement",
"Policy effect" to "Allow", with "Policy resource" to `*`,
    and add the following actions:
    - iot:Connect
    - iot:Publish
    - iot:Subscribe
    - iot:Receive
7. Click on "Create". 

You should now see the policy in the list of policies now.

### Thing Creation

1. Go to the AWS IoT Core console.
2. Click on "Manage" on the left-hand side.
3. Click on "Things".
4. Click on "Create things".
5. Click on "Create single thing".
6. Enter a name for the thing, leave the rest as default, and click on "Next".
7. Select "Auto-generate a new certificate" and move on.
8. Be sure to tick the box on the previously created policy and click on "Create thing".
9. Download the broker certificate, the public key, and the private key.
**Note that** the private key will only be available once, so be sure to download it and store it in a safe place.
***If you suspect that the private key has been compromised, you can revoke the certificate and create a new one, ASAP!***
10. Click on "Done".
11. Copy the certificates and keys to the main directory of the Pico-W.

------------------------------

###### Compartment Screenshot
![model_isometric_view](https://github.com/Charlie-Space-Guardians/micropython_aws_iot/blob/21a44ba03087118815e401b71d7e4fe505ad26c4/Screenshot_2024-02-08-00-20-07_.png)
