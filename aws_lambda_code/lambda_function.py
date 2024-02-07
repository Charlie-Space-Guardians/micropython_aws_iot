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
    db =  boto3.resource('dynamodb')
    table = db.Table(table_name)


    # Extract the MQTT json message from the event
    unix_time = event.get('time_unix')
    mac_address = event.get('mac_address')

    proximity = event.get('proximity')
    ambient_lux = event.get('ambient_lux')



    logger.info('MAC Address:%s', unix_time)
    logger.info('Unix Time:%s', mac_address)
    logger.info('Proximity result:%s', proximity)

    jsonObj = json.loads(json.dumps({
        'unix_time': unix_time,
        'mac_address': mac_address,
        'proximity': proximity,
        'ambient_lux': ambient_lux
        }), parse_float=Decimal)

    #DynamoDB Insert
    table.put_item(Item=jsonObj)

    return {

    }
