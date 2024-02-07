import json
import boto3
import logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client('dynamodb')
table_name = 'python_lambda_iot'


def lambda_handler(event, context):
    # Initialize the DynamoDB instance
    db = boto3.resource('dynamodb')
    table = db.Table(table_name)

    # Extract the MQTT json message from the event
    unix_time = event.get('time_unix')
    mac_address = event.get('mac_address')

    temperature = event.get('temperature')
    pressure = event.get('pressure')
    humidity = event.get('humidity')
    gas = event.get('gas')
    co2 = event.get('co2')

    logger.info('MAC Address:%s', unix_time)
    logger.info('Unix Time:%s', mac_address)
    logger.info('Temperature result:%s', temperature)

    jsonObj = json.loads(json.dumps({
        'unix_time': unix_time,
        'mac_address': mac_address,
        'temperature': temperature,
        'pressure': pressure,
        'humidity': humidity,
        'gas': gas,
        'co2': co2
    }), parse_float=Decimal)

    # DynamoDB Insert
    table.put_item(Item=jsonObj)

    return {

    }