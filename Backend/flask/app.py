import os, sys, json, time, boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from statistics import mean

app = Flask(__name__)
load_dotenv()
CORS(app)

client = boto3.client(
    'dynamodb',
    aws_access_key_id=os.environ['AWS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name='ap-southeast-1'
)
        
DB = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.environ['AWS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name='ap-southeast-1'
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
    date = datetime(2020, 10, 24)
    total_trays = 0
    total_return_trays = 0
    tmr = datetime(2020, 10, 25)
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

def table_calculation(responses, clear_groups):
    got_clear = 0
    total_people = 0
    total_trays = 0
    clean_trays = 0
    outpc = []
    outp = []
    resetc = False
    reset = False
    treset1 = False
    treset2 = False
    start = 0
    end = 0
    start2 = 0
    end2 = 0
    total_time = 0
    tray_ratio = 0.0
    ratio = 0.0
    count = 0
    for i in range(0, len(responses['Items'])):
        item = responses['Items'][i]
        temp_object = item['object'].replace("\'", "\"")
        objects = json.loads(temp_object)
        curr_chairs = 0
        got_table = False
        for obj in objects:
            if obj['object_name'] == "table":
                got_table = True
        if got_table:

            for obj in objects:
                if obj['object_name'] == "chair":
                    curr_chairs += 1
            if curr_chairs >= 4 and resetc == False:
                outpc.append(i - 1)
                end = responses['Items'][i]['ts']
                treset1 = False
                resetc = True
                if end != 0 and start != 0:
                    total_time += (end - start)
                    if (end - start) != 0:
                        count += 1
                    end = 0
                    start = 0
            elif curr_chairs < 4 and treset1 == False:
                treset1 = True
                start = responses['Items'][i]['ts']
                resetc = False
        elif not got_table:
            for obj in objects:
                if obj['object_name'] == "chair":
                    curr_chairs += 1
            if curr_chairs >= 4 and reset == False:
                outp.append(i - 1)
                end2 = responses['Items'][i]['ts']
                treset2 = False
                reset = True
                if end2 != 0 and start2 != 0:
                    total_time += (end2 - start2)
                    if (end2 - start2) != 0:
                        count += 1
                    end2 = 0
                    start2 = 0
            elif curr_chairs < 4 and treset2 == False:
                treset2 = True
                reset = False
                start2 = responses['Items'][i]['ts']
    for i in range(0, len(outpc)):
        chair = 0
        tray = 0
        item = responses['Items'][outpc[i]]
        temp_object = item['object'].replace("\'", "\"")
        objects = json.loads(temp_object)
        for obj in objects:
            if obj['object_name'] == "chair":
                chair += 1
            if obj['object_name'] == "tray":
                tray += 1
        total_people += (4 - chair)
        clear_groups[(4-chair)] += 1
        got_clear += (4 - chair)
        clean_trays += tray
        total_trays += tray
    for i in range(0, len(outp)):
        chair = 0
        tray = 0
        ttray = 0
        cchair = 0
        item = responses['Items'][outp[i]]
        item2 = responses['Items'][outp[i] + 1]
        temp_object = item['object'].replace("\'", "\"")
        temp_object2 = item2['object'].replace("\'", "\"")
        objects = json.loads(temp_object)
        objects2 = json.loads(temp_object2)
        for obj in objects:
            if obj['object_name'] == "chair":
                chair += 1
            if obj['object_name'] == "tray":
                ttray += 1
        for obj2 in objects2:
            if obj2['object_name'] == "tray":
                tray += 1
        total_people += (4 - chair)
        got_clear += ttray - tray
        clean_trays += ttray - tray
        total_trays += ttray
    clear_groups = {0: 0, 1: 1, 2: 1, 3: 4, 4: 4}
    return clear_groups, got_clear, total_people

# RATIO OF PEOPLE THAT CLEAR TABLE
@app.route('/ratio_of_people', methods=['GET'])
def get_ratio_of_people():
    clear_groups = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    table = DB.Table('object_db')
    res = []
    date = datetime(2020, 10, 24, 23, 59, 59)
    prev_day = date - timedelta(days=1)
    responses_1 = table.scan(
        FilterExpression=Key('rpi_id').eq(2)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    responses_2 = table.scan(
        FilterExpression=Key('rpi_id').eq(3)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    clear_groups, got_clear, total_people = table_calculation(responses_1, clear_groups)
    clear_groups, got_clear2, total_people2 = table_calculation(responses_2, clear_groups)
    for i in range(1,5):
        res.append({"size": i, "value": clear_groups[i]})
    got_clear += got_clear2
    total_people += total_people2
    return jsonify({'status':True, "mean": got_clear/total_people, "number_of_people_clear": got_clear, "total_number_of_people": total_people, "groups_clear": res}), 200

#####################################################################################################################
#
# STORE METRIC
#
#####################################################################################################################

# NUMBER OF TRAYS
@app.route("/total_number_trays_leave_store", methods=['GET'])
def tray_leave_store():
    table = DB.Table('qr_db')

    in_store = set([" 1 "," 2 "," 3 "," 4 "," 5 "," 6 "," 7 "," 8 "," 9 "," 10 "])

    date = datetime(2020, 10, 24)
    tmr = datetime(2020, 10, 25)

    responses = table.scan(
        FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))
    )


    count = 0
    trays_returned = 0
    items = responses['Items']

    for item in items:
        count += 1
        qr_id = item['qr_id']
        if qr_id in in_store:
            in_store.remove(qr_id)
        else:
            trays_returned += 1

    return jsonify({"Trays used": count, "Trays returned": trays_returned})

# AVERAGE TIME FOR TRAYS TO RETURN
@app.route("/tray_average_rate", methods=['GET'])
def tray_average_rate():
    table = DB.Table('qr_db')

    time_dictionary = {}
    list_of_times = []

    date = datetime(2020, 10, 24)
    tmr = datetime(2020, 10, 25)

    response = table.scan(
        FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))
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
    date = datetime(2020, 10, 24)
    total_trays = 0
    total_return_trays = 0
    tmr = datetime(2020, 10, 25)
    return_tray_responses_1 = table.scan(
        FilterExpression=Key('rpi_id').eq(4)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))&Attr('store_id').eq(" 1 ")
    )
    return_tray_responses_2 = table.scan(
        FilterExpression=Key('rpi_id').eq(5)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))&Attr('store_id').eq(" 1 ")
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
            FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(date.timestamp() * 1000), round(next_date.timestamp() * 1000))&Attr('store_id').eq(" 1 ")
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


# Time series of trays going out
@app.route('/timeseries_tray_out', methods=['GET'])
def timeseries_tray_out():
    table = DB.Table('qr_db')

    date = datetime(2020, 10, 24)
    in_store = set([" 1 ", " 2 ", " 3 ", " 4 ", " 5 ", " 6 ", " 7 ", " 8 ", " 9 ", " 10 "])
    res = []
    total_trays = 0

    for _ in range(24):
        next_date = date + timedelta(hours=1)
        return_tray_responses = table.scan(
            FilterExpression=Key('rpi_id').eq(1)&Attr('ts').between(round(date.timestamp() * 1000), round(next_date.timestamp() * 1000))
        )
        hour_trays = 0
        for item in return_tray_responses['Items']:
            qr_id = item['qr_id']
            if qr_id in in_store:
                in_store.remove(qr_id)
                hour_trays += 1
            else:
                in_store.add(qr_id)
        total_trays += hour_trays
        date = next_date
        res.append({"ts":round(date.timestamp() * 1000), "value":hour_trays})
    
    return jsonify({'status':True, "value":res, "number_of_trays": total_trays}), 200
#####################################################################################################################
#
# TABLE METRIC
#
#####################################################################################################################

# RATIO OF PEOPLE THAT CLEAR TABLE PER TABLE
@app.route('/ratio_of_people_table', methods=['GET'])
def get_ratio_of_people_table():

    rpi_id = request.args.get('rpi_id', default=None, type=int)

    table = DB.Table('object_db')
    res = []
    date = datetime(2020, 10, 24, 23, 59, 59)
    prev_day = date - timedelta(days=1)
    responses = table.scan(
        FilterExpression=Key('rpi_id').eq(rpi_id)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    got_clear = 0
    total_people = 0
    total_trays = 0
    clean_trays = 0
    outpc = []
    outp=[]
    resetc = False
    reset = False
    treset1 = False
    treset2 = False
    start  = 0
    end = 0
    start2  = 0
    end2 = 0
    total_time = 0 
    tray_ratio = 0.0 
    ratio = 0.0
    count = 0
    for i in range(0, len(responses['Items'])):
        item = responses['Items'][i]
        temp_object = item['object'].replace("\'", "\"")
        objects = json.loads(temp_object)
        curr_chairs = 0
        got_table = False
        for obj in objects:
            if obj['object_name'] == "table":
                got_table = True
        if got_table:
            
            for obj in objects:
                if obj['object_name'] == "chair":
                    curr_chairs += 1
            if curr_chairs >= 4 and resetc == False:
                outpc.append(i-1)
                end  = responses['Items'][i]['ts']
                treset1 = False
                resetc = True
                if end != 0 and start != 0:
                    total_time += (end - start)
                    if (end-start) != 0:
                        count += 1
                    end  = 0
                    start = 0
            elif curr_chairs < 4 and treset1 == False :
                treset1 = True
                start = responses['Items'][i]['ts']
                resetc = False
        elif not got_table:
            for obj in objects:
                if obj['object_name'] == "chair":
                    curr_chairs += 1
            if curr_chairs >= 4 and reset == False:
                outp.append(i-1)
                end2 = responses['Items'][i]['ts']
                treset2 = False
                reset = True
                if end2 != 0 and start2 != 0:
                    total_time += (end2 - start2)
                    if(end2-start2)!=0:
                        count += 1
                    end2  = 0
                    start2 = 0
            elif curr_chairs < 4 and treset2 == False:
                treset2 = True
                reset = False
                start2 = responses['Items'][i]['ts']
    for i in range(0,len(outpc)):
        chair = 0
        tray = 0
        item = responses['Items'][outpc[i]]
        temp_object = item['object'].replace("\'", "\"")
        objects = json.loads(temp_object)
        for obj in objects:
            if obj['object_name'] == "chair":
                chair += 1
            if obj['object_name'] == "tray":
                tray += 1
        total_people += (4-chair)
        got_clear+= (4-chair)
        clean_trays += tray
        total_trays += tray
    for i in range(0,len(outp)):
        chair = 0
        tray = 0
        ttray = 0
        cchair = 0
        item = responses['Items'][outp[i]]
        item2 = responses['Items'][outp[i]+1]
        temp_object = item['object'].replace("\'", "\"")
        temp_object2 = item2['object'].replace("\'", "\"")
        objects = json.loads(temp_object)
        objects2 = json.loads(temp_object2)
        for obj in objects:
            if obj['object_name'] == "chair":
                chair += 1
            if obj['object_name'] == "tray":
                ttray += 1
        for obj2 in objects2:
            if obj2['object_name'] == "tray":
                tray += 1
        total_people += (4-chair)
        got_clear += ttray - tray
        clean_trays += ttray - tray
        total_trays += ttray
    if total_trays != 0:
        tray_ratio = clean_trays/total_trays
    if total_people != 0:
        ratio = got_clear/total_people

    avg_time = float(total_time/(len(outpc)+len(outp)))
    return jsonify({'status':True, "mean": ratio, "number_of_people_clear": got_clear, "total_number_of_people": total_people, "total_trays": total_trays, "ratio_of_trays_return": tray_ratio, "average_time_spent":avg_time}), 200

# TIME SPENT AT TABLE AND TIME TO CLEAN
@app.route('/number_of_tables', methods=['GET'])
def get_number_of_tables():

    rpi_id = request.args.get('rpi_id', default=None, type=int)

    table = DB.Table('object_db')
    res = []
    date = datetime(2020, 10, 24, 23, 59, 59)
    prev_day = date - timedelta(days=1)
    responses = table.scan(
        FilterExpression=Key('rpi_id').eq(rpi_id)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    used_count = 0
    first_seen_table = float('inf')
    total_time_used = 0
    not_clean_count = 0
    prev_seen_people = float('inf')
    total_time_not_clean = 0

    for item in responses['Items']:
        temp_object = item['object'].replace("\'", "\"")
        objects = json.loads(temp_object)
        curr_chairs = 0
        got_table = False
        for obj in objects:
            if obj['object_name'] == "table":
                got_table = True
        if got_table:
            if first_seen_table == float('inf'):
                    first_seen_table = item['ts']
            for obj in objects:
                if obj['object_name'] == "chair":
                    curr_chairs += 1
            if curr_chairs == 4:
                prev_seen_people = float('inf')
        elif not got_table:
            if first_seen_table != float('inf'):
                used_count += 1
                total_time_used += item['ts'] - first_seen_table
                first_seen_table = float('inf')
            for obj in objects:
                if obj['object_name'] == "chair":
                    curr_chairs += 1
            if curr_chairs == 4:
                if prev_seen_people != float('inf'):
                    total_time_not_clean += item['ts'] - prev_seen_people
                    not_clean_count += 1
                    prev_seen_people = float('inf')
            elif curr_chairs != 4:
                prev_seen_people = item['ts']

    used_ratio = 0.0
    if used_count != 0:
        used_ratio = int(total_time_used)/used_count
    not_clean_ratio = 0.0
    if not_clean_count != 0:
        not_clean_ratio = int(total_time_not_clean)/not_clean_count

            
    return jsonify({'status':True, "mean_time_spent": used_count, "mean_time_not_clean": not_clean_ratio}), 200

#####################################################################################################################
#
# RETURN TRAY METRIC
#
#####################################################################################################################

# TODO: Ratio based on distance for that day [[distance, ratio], [distance, ratio]]
@app.route('/store_tray_returned', methods=['GET'])
def store_tray_returned():
    table = DB.Table('qr_db')
    date = datetime(2020, 10, 24)
    tmr = datetime(2020, 10, 25)
    tray_return_close = table.scan(
        FilterExpression=Key('rpi_id').eq(4)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))&Attr('store_id').eq(" 1 ")
    )
    tray_return_further = table.scan(
        FilterExpression=Key('rpi_id').eq(5)&Attr('ts').between(round(date.timestamp() * 1000), round(tmr.timestamp() * 1000))&Attr('store_id').eq(" 1 ")
    )
    result = {"rpi_id": 4, "number_of_trays": tray_return_close['Count']}
    further_result = {"rpi_id": 5, "number_of_trays": tray_return_further['Count']}

    return jsonify({"status": True, "result": [result, further_result]})
    
# TOTAL RATIO OF RETURN TRAYS
@app.route('/number_of_trays', methods=['GET'])
def get_number_of_trays():

    rpi_id = request.args.get('rpi_id', default=None, type=int)

    table = DB.Table('object_db')
    res = []
    date = datetime(2020, 10, 24)
    total_trays = 0
    for _ in range(12):
        next_date = date + timedelta(hours=1)
        return_tray_responses = table.scan(
            FilterExpression=Key('rpi_id').eq(rpi_id)&Attr('ts').between(round(date.timestamp() * 1000), round(next_date.timestamp() * 1000))
        )
        hour_trays = 0
        for item in return_tray_responses['Items']:
            temp_object = item['object'].replace("\'", "\"")
            objects = json.loads(temp_object)
            for obj in objects:
                if obj['object_name'] == "tray":
                    hour_trays += 1
        date = next_date
        total_trays += hour_trays
        res.append({"ts":round(date.timestamp() * 1000), "value":hour_trays})
    
    return jsonify({'status':True, "value":res, "number_of_trays": total_trays}), 200

@app.route('/ratio_of_trays_distance', methods=['GET'])
def get_ratio_of_trays_distance():
    rpi_id = request.args.get('rpi_id', default=None, type=int)
    table = DB.Table('qr_db')
    res = {}
    output={}
    date = datetime(2020, 10, 24, 23, 59, 59)
    prev_day = date - timedelta(days=1)
    count = 0
    total = 0
    responses = table.scan(
        FilterExpression=Key('rpi_id').eq(rpi_id)&Attr('ts').between(round(prev_day.timestamp() * 1000), round(date.timestamp() * 1000))
    )
    for item in responses['Items']:
        if(item['qr_id'] in res):
            res[item['qr_id']].append(item['ts'])
        else:
            res[item['qr_id']]= [item['ts']]
    for trays in res:
        num = len(res.get(trays))
        if(num != 1):
            j = 0
            time=0
            for i in range(1,num):
                time += res.get(trays)[i]-res.get(trays)[j]
                j +=1
            count += num - 1
            output[trays]=time
    for out in output:
        total += output.get(out)
    total = int(float(total))
    ratio = 0
    if count != 0:
        ratio = int(total/count)
    return jsonify({'status':True, "ratio_of_trays_distance": ratio}), 200

#To add to DB
@app.route('/add', methods=['POST'])
def add():
    rpi_id = request.args.get('rpi_id', default=None, type=int)
    table = DB.Table('object_db')
    time = 6
    response = table.put_item(
        Item={
            "rpi_id": 2, "ts":time, "object":"""[{'object_name': 'chair', 'ymin': 206, 'ymax': 257, 'xmin': 592, 'xmax': 640, 'confidence': 0.73486053},
            {'object_name': 'chair', 'ymin': 206, 'ymax': 257, 'xmin': 592, 'xmax': 640, 'confidence': 0.6486053},
            {'object_name': 'chair', 'ymin': 206, 'ymax': 257, 'xmin': 592, 'xmax': 640, 'confidence': 0.6486053},
            {'object_name': 'chair', 'ymin': 206, 'ymax': 257, 'xmin': 592, 'xmax': 640, 'confidence': 0.6486053},
            {'object_name': 'table', 'ymin': 206, 'ymax': 257, 'xmin': 592, 'xmax': 640, 'confidence': 0.53486053}]"""
            }
    )
    return  "true"
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)