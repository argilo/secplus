#!/usr/bin/env python3

import argparse
import csv
import json
import queue
import sys
import threading
import time
import secplus
import serial
import paho.mqtt.client as mqtt


# Settings
MQTT_TOPIC_PREFIX = "home"
HA_DISCOVERY_PREFIX = "homeassistant"
DEVICE_NAME = "GarageDoor"
DEVICE_ID = "1234"
SWITCH_SERIAL = 0xc0deadbeef

# Constants
VERSION = "0.0.1"

# MQTT topics
TOPIC_HA_STATUS = f"{HA_DISCOVERY_PREFIX}/status"
TOPIC_RAW_DATA = f"{MQTT_TOPIC_PREFIX}/{DEVICE_NAME}/raw"
TOPIC_AVAILABILITY = f"{MQTT_TOPIC_PREFIX}/{DEVICE_NAME}/status/availability"
TOPIC_DOOR_DISCOVERY = f"{HA_DISCOVERY_PREFIX}/cover/{DEVICE_NAME}/config"
TOPIC_DOOR_STATUS = f"{MQTT_TOPIC_PREFIX}/{DEVICE_NAME}/status/door"
TOPIC_LIGHT_DISCOVERY = f"{HA_DISCOVERY_PREFIX}/light/{DEVICE_NAME}/config"
TOPIC_LIGHT_COMMAND = f"{MQTT_TOPIC_PREFIX}/{DEVICE_NAME}/command/light"
TOPIC_LIGHT_STATUS = f"{MQTT_TOPIC_PREFIX}/{DEVICE_NAME}/status/light"
TOPIC_LOCK_DISCOVERY = f"{HA_DISCOVERY_PREFIX}/lock/{DEVICE_NAME}/config"
TOPIC_LOCK_COMMAND = f"{MQTT_TOPIC_PREFIX}/{DEVICE_NAME}/command/lock"
TOPIC_LOCK_STATUS = f"{MQTT_TOPIC_PREFIX}/{DEVICE_NAME}/status/lock"
TOPIC_MOTION_DISCOVERY = f"{HA_DISCOVERY_PREFIX}/binary_sensor/{DEVICE_NAME}/config"
TOPIC_MOTION_STATUS = f"{MQTT_TOPIC_PREFIX}/{DEVICE_NAME}/status/motion"

# Wireline command numbers
CMD_GET_STATUS = 0x080
CMD_STATUS = 0x081
CMD_LOCK = 0x18c
CMD_LIGHT = 0x281
CMD_MOTION = 0x285


def ha_discovery_device():
    return {
        "name": "Garage Door Opener",
        "identifiers": f"{DEVICE_NAME}_{DEVICE_ID}",
        "manufacturer": "Clayton Smith",
        "model": "secplus-pi",
        "sw_version": VERSION,
    }


def ha_discovery_door():
    return {
        "name": "Door",
        "device_class": "garage",
        "unique_id": f"{DEVICE_NAME}_{DEVICE_ID}_door",
        "availability_topic": TOPIC_AVAILABILITY,
        # "command_topic": TOPIC_DOOR_COMMAND,
        "state_topic": TOPIC_DOOR_STATUS,
        "device": ha_discovery_device(),
    }


def ha_discovery_light():
    return {
        "name": "Light",
        "unique_id": f"{DEVICE_NAME}_{DEVICE_ID}_light",
        "availability_topic": TOPIC_AVAILABILITY,
        "command_topic": TOPIC_LIGHT_COMMAND,
        "state_topic": TOPIC_LIGHT_STATUS,
        "device": ha_discovery_device(),
    }


def ha_discovery_lock():
    return {
        "name": "Lock",
        "unique_id": f"{DEVICE_NAME}_{DEVICE_ID}_lock",
        "availability_topic": TOPIC_AVAILABILITY,
        "command_topic": TOPIC_LOCK_COMMAND,
        "state_topic": TOPIC_LOCK_STATUS,
        "device": ha_discovery_device(),
    }


def ha_discovery_motion():
    return {
        "name": "Motion",
        "device_class": "motion",
        "unique_id": f"{DEVICE_NAME}_{DEVICE_ID}_motion",
        "availability_topic": TOPIC_AVAILABILITY,
        "state_topic": TOPIC_MOTION_STATUS,
        "device": ha_discovery_device(),
    }


def send_serial(ser, command, payload):
    try:
        with open("rolling.txt") as f:
            rolling = int(f.read())
    except FileNotFoundError:
        rolling = 0

    rolling += 1

    with open("rolling.txt", "w") as f:
        f.write(str(rolling))

    packet = secplus.encode_wireline_command(rolling, SWITCH_SERIAL, command, payload)

    ser.break_condition = True
    time.sleep(0.001675)
    ser.break_condition = False
    ser.write(packet)


def serial_thread(finished, serial_queue, mqttc):
    PREAMBLE = bytes([0x55, 0x01, 0x00])
    ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=0.1)

    with open("packets.csv", "a") as f:
        writer = csv.writer(f)

        last_motion = None
        while not finished.is_set():
            if last_motion is not None and time.monotonic() > last_motion + 15:
                mqttc.publish(TOPIC_MOTION_STATUS, "OFF", retain=True)
                last_motion = None

            read_state = 0
            while True:
                if read_state < 3:
                    data = ser.read()
                    if len(data) < 1:
                        break

                    if data == PREAMBLE[read_state:read_state+1]:
                        read_state += 1
                    else:
                        read_state = 0
                else:
                    data = ser.read(16)
                    if len(data) < 16:
                        break

                    end_time = time.time()
                    packet = PREAMBLE + data

                    try:
                        mqttc.publish(TOPIC_RAW_DATA, packet)
                        rolling, device_id, command, payload = secplus.decode_wireline_command(packet)

                        pretty = secplus.pretty_wireline(rolling, device_id, command, payload)

                        time_str = f"{end_time:.3f}"
                        writer.writerow([time_str, packet.hex(), pretty])
                        f.flush()
                        print(f"{time_str} {pretty}", flush=True)

                        if device_id != SWITCH_SERIAL:
                            if command == CMD_STATUS:
                                door_status = payload >> 16
                                if door_status in secplus._DOOR_STATUS:
                                    door_status_string = secplus._DOOR_STATUS[door_status]
                                    mqttc.publish(TOPIC_DOOR_STATUS, door_status_string, retain=True)
                                light = (payload >> 1) & 1
                                mqttc.publish(TOPIC_LIGHT_STATUS, "ON" if light else "OFF", retain=True)
                                lock = payload & 1
                                mqttc.publish(TOPIC_LOCK_STATUS, "LOCKED" if lock else "UNLOCKED", retain=True)
                            if command == CMD_LIGHT:
                                serial_queue.put((CMD_GET_STATUS, 0x00001))
                            if command == CMD_MOTION:
                                last_motion = time.monotonic()
                                mqttc.publish(TOPIC_MOTION_STATUS, "ON", retain=True)
                                serial_queue.put((CMD_GET_STATUS, 0x00001))
                    except ValueError as e:
                        print(e, flush=True)

                    read_state = 0

            # No serial data received for 100 ms, so send the next packet
            try:
                command, payload = serial_queue.get_nowait()
                print(f"{time.time():.3f} Sending {command:03x} {payload:05x}")
                send_serial(ser, command, payload)
            except queue.Empty:
                pass

    ser.close()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect to MQTT: {reason_code}")
    else:
        client.publish(TOPIC_AVAILABILITY, "online", retain=True)
        client.subscribe(TOPIC_HA_STATUS)
        client.subscribe(TOPIC_LIGHT_COMMAND)
        client.subscribe(TOPIC_LOCK_COMMAND)


def on_message(client, serial_queue, message):
    if message.topic == TOPIC_HA_STATUS:
        if message.payload == b"online":
            client.publish(TOPIC_DOOR_DISCOVERY, json.dumps(ha_discovery_door()))
            client.publish(TOPIC_LIGHT_DISCOVERY, json.dumps(ha_discovery_light()))
            client.publish(TOPIC_LOCK_DISCOVERY, json.dumps(ha_discovery_lock()))
            client.publish(TOPIC_MOTION_DISCOVERY, json.dumps(ha_discovery_motion()))
    elif message.topic == TOPIC_LIGHT_COMMAND:
        serial_queue.put((CMD_LIGHT, 0x20000))
        serial_queue.put((CMD_GET_STATUS, 0x00001))
    elif message.topic == TOPIC_LOCK_COMMAND:
        serial_queue.put((CMD_LOCK, 0x20000))


parser = argparse.ArgumentParser(prog="secplus-pi",
                                 description="Expose a garage door opener as a HomeAssistant-compatible MQTT device",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-H', default="homeassistant.local", metavar="host", help="MQTT broker hostname")
parser.add_argument('-u', metavar="username", help="MQTT username")
parser.add_argument('-p', metavar="username", help="MQTT password")
args = parser.parse_args()

serial_queue = queue.Queue()
serial_queue.put((CMD_GET_STATUS, 0x00001))
serial_queue.put((CMD_GET_STATUS, 0x00001))

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=serial_queue)
if args.u and args.p:
    mqttc.username_pw_set(args.u, args.p)
mqttc.will_set(TOPIC_AVAILABILITY, "offline", retain=True)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
while True:
    try:
        mqttc.connect(args.H)
        break
    except OSError as e:
        print(f"Error connecting to MQTT broker. Will retry in 5 seconds. {e}")
        time.sleep(5)
mqttc.loop_start()

finished = threading.Event()
receive_thread = threading.Thread(target=serial_thread, args=(finished, serial_queue, mqttc))
receive_thread.start()

if sys.stdin.isatty():
    while True:
        try:
            message = input()
        except KeyboardInterrupt:
            break

        parts = message.split()
        if len(parts) != 2:
            print("Invalid input")
            continue

        try:
            command = int(parts[0], 16)
            payload = int(parts[1], 16)
            serial_queue.put((command, payload))
        except ValueError:
            print("Invalid input")
            continue

    finished.set()

receive_thread.join()

mqttc.publish(TOPIC_AVAILABILITY, "offline", retain=True)
mqttc.disconnect()
mqttc.loop_stop()
