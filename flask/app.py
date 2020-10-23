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

#####################################################################################################################
#
# GENERAL METRIC
#
#####################################################################################################################

# TOTAL RATIO OF RETURN TRAYS
@app.route('/ratio_of_trays', methods=['GET'])
def get_ratio_of_trays():

    table = DB.Table('qr_db')
    trays = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0}
    res = []
    date = datetime(2020, 10, 23)
    total_trays = 0
    total_return_trays = 0
    tmr = datetime(2020, 10, 24)
    return_tray_responses_1 = table.scan(
        FilterExpression=Key('rpi_id').eq(4)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))
    )
    return_tray_responses_2 = table.scan(
        FilterExpression=Key('rpi_id').eq(5)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))
    )
    for item in return_tray_responses_1['Items']:
        qr_id = int(item['qr_id'])
        trays[qr_id] += 1
    for item in return_tray_responses_2['Items']:
        qr_id = int(item['qr_id'])
        trays[qr_id] += 1
    for _ in range(24):
        next_date = date + timedelta(hours=1)
        store_responses = table.scan(
            FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(date.timestamp() * 1000), round(next_date.timestamp() * 1000))
        )
        hour_return_trays = 0
        hour_tray = 0
        for item in store_responses['Items']:
            qr_id = int(item['qr_id'])
            if trays[qr_id] != 0:
                hour_return_trays += 1
                trays[qr_id] -= 1
            hour_tray += 1
        if hour_tray == 0:
            ratio = 0.0
        else:
            ratio = hour_return_trays/hour_tray
        date = next_date
        total_trays += hour_tray
        total_return_trays += hour_return_trays
        res.append({"ts":round(date.timestamp() * 1000), "value":ratio})
    
    return jsonify({'status':True, "value":res, "mean": total_return_trays/total_trays}), 200

# RATIO OF PEOPLE THAT CLEAR TABLE
@app.route('/ratio_of_people', methods=['GET'])
def get_ratio_of_people():

    table = DB.Table('object_db')
    res = []
    date = datetime(2020, 10, 23, 23, 59, 59)
    prev_day = date - timedelta(days=1)
    responses_1 = table.scan(
        FilterExpression=Key('rpi_id').eq(2)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    responses_2 = table.scan(
        FilterExpression=Key('rpi_id').eq(3)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    responses = responses_1['Items'] + responses_2['Items']
    got_clear = 0
    total_people = 0
    last_seen_table = float('inf')
    prev_seen_chairs = 4

    for item in responses:
        temp_object = item['object'].replace("\'", "\"")
        objects = json.loads(temp_object)
        curr_chairs = 0
        got_table = False
        for obj in objects:
            if obj['object_name'] == "table":
                last_seen_table = item['ts']
                got_table = True
        if got_table:
            for obj in objects:
                if obj['object_name'] == "chair":
                    curr_chairs += 1
            if curr_chairs == 4:
                got_clear += curr_chairs - prev_seen_chairs
                total_people += curr_chairs - prev_seen_chairs
                prev_seen_chairs = curr_chairs
        elif not got_table:
            for obj in objects:
                if obj['object_name'] == "chair":
                    curr_chairs += 1
            if curr_chairs == 4:
                total_people += curr_chairs - prev_seen_chairs
                prev_seen_chairs = curr_chairs
            else:
                prev_seen_chairs = curr_chairs
            
    return jsonify({'status':True, "mean": got_clear/total_people, "number_of_people_clear": got_clear, "total_number_of_people": total_people}), 200

# TODO: [[storeID, ratio],[storeID, ratio]]
# @app.route('/ratio_of_trays_store_1', methods=['GET'])
# def get_ratio_of_trays_store_1():

#     table = DB.Table('Qr_Table')
#     res = []
#     date = datetime.utcnow() + timedelta(hours=8)
#     prev_day = date - timedelta(days=1)
#     store_1_responses = table.scan(
#         FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
#     )
#     store_2_responses = table.scan(
#         FilterExpression=Key('rpi_id').eq(2)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
#     )
#     return_tray_responses_store_1 = table.scan(
#         FilterExpression=Key('rpi_id').eq(3)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))&Attr('store_id').eq(" 1 ")
#     )
#     return_tray_responses_store_2 = table.scan(
#         FilterExpression=Key('rpi_id').eq(3)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))&Attr('store_id').eq(" 2 ")
#     )
#     store_1 = set()
#     store_2 = set()
#     return_tray_store_1 = set()
#     return_tray_store_2 = set()
#     for item in store_1_responses['Items']:
#         qr_id = int(item['qr_id'])
#         store_1.add(qr_id)
#     for item in store_2_responses['Items']:
#         qr_id = int(item['qr_id'])
#         store_2.add(qr_id)
#     for item in return_tray_responses_store_1['Items']:
#         qr_id = int(item['qr_id'])
#         return_tray_store_1.add(qr_id)
#     for item in return_tray_responses_store_2['Items']:
#         qr_id = int(item['qr_id'])
#         return_tray_store_2.add(qr_id)
    
#     return jsonify({'status':True, "ts":round(date.timestamp() * 1000), "value":[{"store_id": 1, "ratio": len(return_tray_store_1)/len(store_1)}, {"store_id": 2, "ratio": len(return_tray_store_2)/len(store_2)}]}), 200

# TODO: [[1, ratio],[2, ratio], [3, ratio], [4,ratio]]
@app.route('/group_size', methods=['GET'])
def get_group_size():

    client = boto3.client('dynamodb')
    DB = boto3.resource('dynamodb')

    table = DB.Table('test')
    
    return jsonify({'status':True, "message":"test"}), 200

#Number of trays that leave the store and number of trays that were returned
@app.route("/trays_leave_store", methods=['GET'])
def tray_leave_store():
    table = DB.Table('qr_db')

    in_store = set([" 1 "," 2 "," 3 "," 4 "," 5 "," 6 "," 7 "," 8 "," 9 "," 10 "])

    responses = table.scan(
        FilterExpression=Key('rpi_id').eq(1)
    )

    count = 0
    trays_returned = 0
    items = responses['Items']

    for item in items:
        qr_id = item['qr_id']
        if qr_id in in_store:
            count += 1
            in_store.remove(qr_id)
        else:
            in_store.add(qr_id)
            trays_returned += 1

    return jsonify({"Trays used": count, "Trays returned": trays_returned})

#Don't need this but just keep in codebase
# def tray_calculation(item_list):
#     if len(item_list) != 0:
#         first = item_list[0]
#         timings = []
#         for i in range(1,len(item_list)):
#             timings.append(item_list[i]['ts'] - first['ts'])
#             first = item_list[i]
#
#         return float(mean(timings)), float(sum(timings))
#
#     return 0,0

# AVERAGE TIME FOR TRAYS TO RETURN
@app.route("/tray_average_rate", methods=['GET'])
def tray_average_rate():
    table = DB.Table('qr_db')

    time_dictionary = {}
    list_of_times = []

    response = table.scan(
        FilterExpression=Key('rpi_id').eq(1)
    )

    items = response['Items']

    for item in items:
        if item['qr_id'] not in time_dictionary:
            time_dictionary[item['qr_id']] = item['ts']
        else:
            time_difference = abs(item['ts'] - time_dictionary[item['qr_id']])
            list_of_times.append(time_difference)
            time_dictionary[item['qr_id']] = item['ts']

    average_time = 0
    if len(list_of_times) != 0:
        average_time = float(mean(list_of_times))

    return jsonify({"result": average_time})

# RATIO OF TRAY RETURN
@app.route('/ratio_of_trays_store', methods=['GET'])
def get_ratio_of_trays_store():

    store_id = request.args.get('store_id', default=None, type=str)

    table = DB.Table('qr_db')
    trays = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0}
    res = []
    date = datetime(2020, 10, 23)
    total_trays = 0
    total_return_trays = 0
    tmr = datetime(2020, 10, 24)
    return_tray_responses_1 = table.scan(
        FilterExpression=Key('rpi_id').eq(4)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))&Attr('store_id').eq(f" {store_id} ")
    )
    return_tray_responses_2 = table.scan(
        FilterExpression=Key('rpi_id').eq(5)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))&Attr('store_id').eq(f" {store_id} ")
    )
    for item in return_tray_responses_1['Items']:
        qr_id = int(item['qr_id'])
        trays[qr_id] += 1
    for item in return_tray_responses_2['Items']:
        qr_id = int(item['qr_id'])
        trays[qr_id] += 1
    for _ in range(24):
        next_date = date + timedelta(hours=1)
        store_responses = table.scan(
            FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(date.timestamp() * 1000), round(next_date.timestamp() * 1000))&Attr('store_id').eq(f" {store_id} ")
        )
        hour_return_trays = 0
        hour_tray = 0
        for item in store_responses['Items']:
            qr_id = int(item['qr_id'])
            if trays[qr_id] != 0:
                hour_return_trays += 1
                trays[qr_id] -= 1
            hour_tray += 1
        if hour_tray == 0:
            ratio = 0.0
        else:
            ratio = hour_return_trays/hour_tray
        date = next_date
        total_trays += hour_tray
        total_return_trays += hour_return_trays
        res.append({"ts":round(date.timestamp() * 1000), "value":ratio})
    
    return jsonify({'status':True, "value":res, "mean": total_return_trays/total_trays}), 200


#####################################################################################################################
#
# TABLE METRIC
#
#####################################################################################################################

# RATIO OF PEOPLE THAT CLEAR TABLE PER TABLE
@app.route('/ratio_of_people_table', methods=['GET'])
def get_ratio_of_people_table():

    rpi_id = request.args.get('rpi_id', default=None, type=str)

    table = DB.Table('object_db')
    res = []
    date = datetime(2020, 10, 23, 23, 59, 59)
    prev_day = date - timedelta(days=1)
    responses = table.scan(
        FilterExpression=Key('rpi_id').eq(rpi_id)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    got_clear = 0
    total_people = 0
    last_seen_table = float('inf')
    prev_seen_chairs = 4

    for item in responses['Items']:
        temp_object = item['object'].replace("\'", "\"")
        objects = json.loads(temp_object)
        curr_chairs = 0
        got_table = False
        for obj in objects:
            if obj['object_name'] == "table":
                last_seen_table = item['ts']
                got_table = True
        if got_table:
            for obj in objects:
                if obj['object_name'] == "chair":
                    curr_chairs += 1
            if curr_chairs == 4:
                got_clear += curr_chairs - prev_seen_chairs
                total_people += curr_chairs - prev_seen_chairs
                prev_seen_chairs = curr_chairs
        elif not got_table:
            for obj in objects:
                if obj['object_name'] == "chair":
                    curr_chairs += 1
            if curr_chairs == 4:
                total_people += curr_chairs - prev_seen_chairs
                prev_seen_chairs = curr_chairs
            else:
                prev_seen_chairs = curr_chairs
            
    return jsonify({'status':True, "mean": got_clear/total_people, "number_of_people_clear": got_clear, "total_number_of_people": total_people}), 200

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

#####################################################################################################################
#
# RETURN TRAY METRIC
#
#####################################################################################################################

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

# Time series of trays going out
@app.route('/timeseries_tray_out', methods=['GET'])
def timeseries_tray_out():

    table = DB.Table('qr_db')

    date = datetime(2020, 10, 23)
 
    tmr = datetime(2020, 10, 24)

    time_dict = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0 ,12:0, 13:0, 14:0, 15:0, 16:0, 17:0, 18:0, 19:0, 20:0, 21:0, 22:0, 23:0}

    in_store = set([" 1 "," 2 "," 3 "," 4 "," 5 "," 6 "," 7 "," 8 "," 9 "," 10 "])

    response = table.scan(
        FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))
    )

    for item in response['Items']:
        qr_id = item['qr_id']
        if qr_id in in_store:
            in_store.remove(qr_id)
            hour = abs(item['ts'] - round(date.timestamp() * 1000)) // 3600000
            try:
                time_dict[hour] += 1
            except:
                pass

        else:
            in_store.add(qr_id)

    return jsonify({"result": time_dict})



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)