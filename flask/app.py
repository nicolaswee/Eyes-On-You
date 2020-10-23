import os, sys, json, time, boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
CORS(app)

client = boto3.client(
    'dynamodb',
    aws_access_key_id=os.environ['AWS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
        
DB = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.environ['AWS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
)

# TODO: Per day per hour
@app.route('/ratio_of_trays', methods=['GET'])
def get_ratio_of_trays():

    table = DB.Table('Qr_Table')
    res = []
    date = datetime.utcnow() + timedelta(hours=8)
    total_trays = 0
    total_return_trays = 0
    for _ in range(24):
        prev_day = date - timedelta(hours=1)
        store_responses = table.scan(
            FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
        )
        return_tray_responses = table.scan(
            FilterExpression=Key('rpi_id').eq(2)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
        )
        store = set()
        return_tray = set()
        for item in store_responses['Items']:
            qr_id = int(item['qr_id'])
            store.add(qr_id)
        for item in return_tray_responses['Items']:
            qr_id = int(item['qr_id'])
            return_tray.add(qr_id)
        date = prev_day
        if len(store) == 0:
            ratio = 0.0
        else:
            ratio = len(return_tray)/len(store)
        total_trays += len(store)
        total_return_trays += len(return_tray)
        res.append({"ts":round(date.timestamp() * 1000), "value":ratio})
    
    return jsonify({'status':True, "value":res, "mean": total_return_trays/total_trays}), 200

# TODO: Just the ratio for the day
@app.route('/ratio_of_people', methods=['GET'])
def get_ratio_of_people():

    table = DB.Table('Object_Table')
    res = []
    date = datetime.utcnow() + timedelta(hours=8)
    prev_day = date - timedelta(days=1)
    responses = table.scan(
        FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    never_clear = 0
    total_people = 0
    last_seen_table = float('inf')
    prev_seen_people = 0

    for item in responses['Items']:
        objects = json.loads(item['objects'])
        curr_people = 0
        got_table = False
        if item['ts'] - last_seen_table > 30000:
            for obj in objects:
                if obj['object'] == "table":
                    last_seen_table = obj['ts']
                    got_table = True
                elif obj['object'] == "person":
                    curr_people += 1
                    total_people += 1
            if not got_table and curr_people == 0:
                never_clear += prev_seen_people
            if not got_table and curr_people != prev_seen_people:
                prev_seen_people = curr_people
        else:
            for obj in objects:
                if obj['object'] == "table":
                    last_seen_table = obj['ts']
            
    return jsonify({'status':True, "message":"test"}), 200

# TODO: Ratio based on distance for that day [[distance, ratio], [distance, ratio]]
@app.route('/ratio_of_people_distance', methods=['GET'])
def get_ratio_of_people_distance():

    table = DB.Table('Object_Table')
    res = []
    date = datetime.utcnow() + timedelta(hours=8)
    prev_day = date - timedelta(hours=1)
    responses = table.scan(
        FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    never_clear = 0
    total_people = 0
    last_seen_table = float('inf')
    prev_seen_people = 0
    
    for item in responses['Items']:
        objects = json.loads(item['objects'])
        curr_people = 0
        got_table = False
        if item['ts'] - last_seen_table > 30000:
            for obj in objects:
                if obj['object'] == "table":
                    last_seen_table = obj['ts']
                    got_table = True
                elif obj['object'] == "person":
                    curr_people += 1
                    total_people += 1
            if not got_table and curr_people == 0:
                never_clear += prev_seen_people
            if not got_table and curr_people != prev_seen_people:
                prev_seen_people = curr_people
        else:
            for obj in objects:
                if obj['object'] == "table":
                    last_seen_table = obj['ts']
            
    return jsonify({'status':True, "message":"test"}), 200

# TODO: [[storeID, ratio],[storeID, ratio]]
@app.route('/ratio_of_trays_store', methods=['GET'])
def get_ratio_of_trays_store():

    table = DB.Table('Qr_Table')
    res = []
    date = datetime.utcnow() + timedelta(hours=8)
    prev_day = date - timedelta(days=1)
    store_1_responses = table.scan(
        FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    store_2_responses = table.scan(
        FilterExpression=Key('rpi_id').eq(2)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    return_tray_responses_store_1 = table.scan(
        FilterExpression=Key('rpi_id').eq(3)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))&Attr('store_id').eq(" 1 ")
    )
    return_tray_responses_store_2 = table.scan(
        FilterExpression=Key('rpi_id').eq(3)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))&Attr('store_id').eq(" 2 ")
    )
    store_1 = set()
    store_2 = set()
    return_tray_store_1 = set()
    return_tray_store_2 = set()
    for item in store_1_responses['Items']:
        qr_id = int(item['qr_id'])
        store_1.add(qr_id)
    for item in store_2_responses['Items']:
        qr_id = int(item['qr_id'])
        store_2.add(qr_id)
    for item in return_tray_responses_store_1['Items']:
        qr_id = int(item['qr_id'])
        return_tray_store_1.add(qr_id)
    for item in return_tray_responses_store_2['Items']:
        qr_id = int(item['qr_id'])
        return_tray_store_2.add(qr_id)
    
    return jsonify({'status':True, "ts":round(date.timestamp() * 1000), "value":[{"store_id": 1, "ratio": len(return_tray_store_1)/len(store_1)}, {"store_id": 2, "ratio": len(return_tray_store_2)/len(store_2)}]}), 200
# TODO: 
@app.route('/number_of_tables', methods=['GET'])
def get_number_of_tables():

    table = DB.Table('Qr_Table')
    res = []
    date = datetime.utcnow() + timedelta(hours=8)
    for _ in range(7):
        prev_day = date - timedelta(days=1)
        store_responses = table.scan(
            FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
        )
        return_tray_responses = table.scan(
            FilterExpression=Key('rpi_id').eq(2)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
        )
        store = set()
        return_tray = set()
        items = store_responses['Items']
        for item in items:
            qr_id = int(item['qr_id'])
            store.add(qr_id)
        items = return_tray_responses['Items']
        for item in items:
            qr_id = int(item['qr_id'])
            return_tray.add(qr_id)
        date = prev_day
        if len(store) == 0:
            ratio = 0
        else:
            ratio = len(return_tray)/len(store)
        res.append({"ts":round(date.timestamp() * 1000), "value":ratio})
    
    return jsonify({'status':True, "value":res}), 200

# TODO: [[1, ratio],[2, ratio], [3, ratio], [4,ratio]]
@app.route('/group_size', methods=['GET'])
def get_group_size():

    client = boto3.client('dynamodb')
    DB = boto3.resource('dynamodb')

    table = DB.Table('test')
    
    return jsonify({'status':True, "message":"test"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)