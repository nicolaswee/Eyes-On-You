import os, sys, json, time, boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from statistics import mean

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
    # date = datetime.utcnow() + timedelta(hours=8)
    date = datetime(2020, 10, 23, 23, 59, 59)
    total_trays = 0
    total_return_trays = 0
    for _ in range(24):
        prev_date = date - timedelta(hours=1)
        store_responses = table.scan(
            FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(prev_date.timestamp() * 1000), round(date.timestamp() * 1000))
        )
        return_tray_responses = table.scan(
            FilterExpression=Key('rpi_id').eq(2)&Attr('ts').between(round(prev_date.timestamp() * 1000), round(date.timestamp() * 1000))
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

@app.route("/total_number_trays_leave_store", methods=['GET'])
def tray_leave_store():
    table = DB.Table('Qr_Table')

    in_store = set([" 1 "," 2 "," 3 "," 4 "," 5 "," 6 "," 7 "," 8 "," 9 "," 10 "])

    responses = table.scan(
        FilterExpression=Key('rpi_id').eq(1)
    )

    count = 0

    items = responses['Items']

    for item in items:
        qr_id = item['qr_id']
        if qr_id in in_store:
            count += 1
            in_store.remove(qr_id)
        else:
            in_store.add(qr_id)

    return jsonify({"Number of trays": count - 1})

def tray_calculation(item_list):
    if len(item_list) != 0:
        first = item_list[0]
        timings = []
        for i in range(1,len(item_list)):
            timings.append(item_list[i]['ts'] - first['ts'])
            first = item_list[i]

        return float(mean(timings)), float(sum(timings))

    return 0,0

@app.route("/tray_average_rate", methods=['GET'])
def tray_average_rate():
    table = DB.Table('Qr_Table')
    total_tray = 0
    total_time = 0
    response_qr_1 = table.scan(
        FilterExpression=Key('rpi_id').eq(1) & Attr('qr_id').eq(" 1 ")
    )

    qr_1_average, qr_1_total = tray_calculation(response_qr_1['Items'])
    total_tray += response_qr_1['Count']
    qr_1 = {"qr_1_average": qr_1_average, "qr_1_total": qr_1_total}
    total_time += qr_1_total

    response_qr_2 = table.scan(
        FilterExpression=Key('rpi_id').eq(1) & Attr('qr_id').eq(" 2 ")
    )
    total_tray += response_qr_2['Count']
    qr_2_average, qr_2_total = tray_calculation(response_qr_2['Items'])
    qr_2 = {"qr_2_average": qr_2_average, "qr_2_total": qr_2_total}
    total_time += qr_2_total

    response_qr_3 = table.scan(
        FilterExpression=Key('rpi_id').eq(1) & Attr('qr_id').eq(" 3 ")
    )

    total_tray += response_qr_3['Count']
    qr_3_average, qr_3_total = tray_calculation(response_qr_3['Items'])
    qr_3 = {"qr_3_average": qr_3_average, "qr_3_total": qr_3_total}
    total_time += qr_3_total

    response_qr_4 = table.scan(
        FilterExpression=Key('rpi_id').eq(1) & Attr('qr_id').eq(" 4 ")
    )

    total_tray += response_qr_4['Count']
    qr_4_average, qr_4_total = tray_calculation(response_qr_4['Items'])
    qr_4 = {"qr_4_average": qr_4_average, "qr_4_total": qr_4_total}
    total_time += qr_4_total

    response_qr_5 = table.scan(
        FilterExpression=Key('rpi_id').eq(1) & Attr('qr_id').eq(" 5 ")
    )

    total_tray += response_qr_5['Count']
    qr_5_average, qr_5_total = tray_calculation(response_qr_5['Items'])
    qr_5 = {"qr_5_average": qr_5_average, "qr_5_total": qr_5_total}
    total_time += qr_5_total

    response_qr_6 = table.scan(
        FilterExpression=Key('rpi_id').eq(1) & Attr('qr_id').eq(" 6 ")
    )

    total_tray += response_qr_6['Count']
    qr_6_average, qr_6_total = tray_calculation(response_qr_6['Items'])
    qr_6 = {"qr_6_average": qr_6_average, "qr_6_total": qr_6_total}
    total_time += qr_6_total

    response_qr_7 = table.scan(
        FilterExpression=Key('rpi_id').eq(1) & Attr('qr_id').eq(" 7 ")
    )

    total_tray += response_qr_7['Count']
    qr_7_average, qr_7_total = tray_calculation(response_qr_7['Items'])
    qr_7 = {"qr_7_average": qr_7_average, "qr_7_total": qr_7_total}
    total_time += qr_7_total

    response_qr_8 = table.scan(
        FilterExpression=Key('rpi_id').eq(1) & Attr('qr_id').eq(" 8 ")
    )

    total_tray += response_qr_8['Count']
    qr_8_average, qr_8_total = tray_calculation(response_qr_8['Items'])
    qr_8 = {"qr_8_average": qr_8_average, "qr_8_total": qr_8_total}
    total_time += qr_8_total

    response_qr_9 = table.scan(
        FilterExpression=Key('rpi_id').eq(1) & Attr('qr_id').eq(" 9 ")
    )

    total_tray += response_qr_9['Count']
    qr_9_average, qr_9_total = tray_calculation(response_qr_9['Items'])
    qr_9 = {"qr_9_average": qr_9_average, "qr_9_total": qr_9_total}
    total_time += qr_9_total
    response_qr_10 = table.scan(
        FilterExpression=Key('rpi_id').eq(1) & Attr('qr_id').eq(" 10 ")
    )

    total_tray += response_qr_10['Count']
    qr_10_average, qr_10_total = tray_calculation(response_qr_10['Items'])
    qr_10 = {"qr_10_average": qr_10_average, "qr_10_total": qr_10_total}
    total_time += qr_10_total

    return jsonify({"result": [qr_1, qr_2, qr_3, qr_4, qr_5, qr_6, qr_7, qr_8, qr_9, qr_10], "total_tray": total_tray})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)