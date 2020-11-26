#!/usr/bin/env python
# coding: utf-8
"""
Object Detection (On Pi Camera) From TF2 Saved Model
=====================================
"""

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    
import os, pathlib, cv2, argparse, socket, ssl, string, json, time, datetime, warnings
import tensorflow as tf
from threading import Thread
import paho.mqtt.client as paho
from pyzbar import pyzbar
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import numpy as np
import matplotlib.pyplot as plt

tf.get_logger().setLevel('ERROR')           
connflag = False
def on_connect(client, userdata, flags, rc):                                        # func for making connection
    global connflag
    connflag = True
 
def on_message(client, userdata, msg):                                              # Func for Sending msg
    print(msg.topic+" "+str(msg.payload))
    
mqttc = paho.Client()                                                               # mqttc object
mqttc.on_connect = on_connect                                                       # assign on_connect func
mqttc.on_message = on_message
awshost = "AWS_ENDPOINT"                     # Endpoint
awsport = 8883                                                                      # Port no.   
clientId = "IoTProject_client"                                                      # Thing_Name
thingName = "IoTProject_client"                                                     # Thing_Name
caPath = "/home/pi/Downloads/AmazonRootCA1.pem"                                     # Root_CA_Certificate_Name
certPath = "/home/pi/Downloads/f6b9562445-certificate.pem.crt"                      # <Thing_Name>.cert.pem
keyPath = "/home/pi/Downloads/f6b9562445-private.pem.key"                           # <Thing_Name>.private.key

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)  # pass parameters
mqttc.connect(awshost, awsport, keepalive=60)                                       # connect to aws server
mqttc.loop_start()

class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(640,480),framerate=30):
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        

parser = argparse.ArgumentParser()
parser.add_argument('--model', help='Folder that the Saved Model is Located In', default='exported-models/my_mobilenet_model')
parser.add_argument('--labels', help='Where the Labelmap is Located', default='models/research/object_detection/data/mscoco_label_map.pbtxt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects', default=0.7)
                    
args = parser.parse_args()
PATH_TO_MODEL_DIR = args.model
PATH_TO_LABELS = args.labels
MIN_CONF_THRESH = float(args.threshold)

# from object_detection.utils import label_map_util
# from object_detection.utils import visualization_utils as viz_utils
PATH_TO_SAVED_MODEL = PATH_TO_MODEL_DIR + "/saved_model"
print('Loading model...', end='')
start_time = time.time()
detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
end_time = time.time()
elapsed_time = end_time - start_time
print('Done! Took {} seconds'.format(elapsed_time))
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
# import numpy as np
# import matplotlib.pyplot as plt
# import warnings
warnings.filterwarnings('ignore')   

print('Running inference for PiCamera')
videostream = VideoStream(resolution=(640,480),framerate=30).start()
while True:
    ##sleep(3)
    frame = videostream.read()
    barcodes = pyzbar.decode(frame)
    if(barcodes):
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(frame, text, (x, y - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        if connflag == True:
            bId1 = barcodeData
            rpiId = 1
            QrName= barcodeData.split(",")
            qr_id = int(QrName[0])
            store_id= int(QrName[1]) 
            # paylodmsg0="{"
            # paylodmsg1="\"rpi_id\":"
            # paylodmsg2=",\"qr_id\":\""
            # paylodmsg3="\",\"store_id\":\""
            # paylodmsg4="\"}"
            # paylodmsg = "{} {} {} {} {} {} {} {}".format(paylodmsg0, paylodmsg1, rpiId, paylodmsg2, qr_id, paylodmsg3, store_id, paylodmsg4)
            # paylodmsg = json.dumps(paylodmsg) 
            # paylodmsg_json = json.loads(paylodmsg)
            payloadmsg = {"rpi_id": rpiId, "qr_id": qr_id, "store_id": store_id}
            # Send to MQTT only when there is a change in QR code
            mqttc.publish("Qr", json.dumps(payloadmsg), qos=1)
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF
    else: 
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_expanded = np.expand_dims(frame_rgb, axis=0)
        imH, imW, _ = frame.shape
        input_tensor = tf.convert_to_tensor(frame)[tf.newaxis, ...]
        # input_tensor = input_tensor[tf.newaxis, ...]
        detections = detect_fn(input_tensor)
        # num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy()
                       for key, value in detections.items()}
        detections['num_detections'] = int(detections.pop('num_detections'))
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
        # detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
        scores = detections['detection_scores']
        boxes = detections['detection_boxes']
        classes = detections['detection_classes']
        count = 0
        output = []
        for i in range(len(scores)):
            if (scores[i] > MIN_CONF_THRESH):
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))
                # confidence = scores[i]
                cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
                object_name = category_index[int(classes[i])]['name'] # Look up object name from "labels" array using class index
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
                objdict={"object_name": object_name, "ymin": ymin, "ymax": ymax, "xmin": xmin, "xmax": xmax, "confidence": scores[i]}
                # objdict["object_name"]=object_name
                # objdict["ymin"]=ymin
                # objdict["ymax"]=ymax
                # objdict["xmin"]=xmin
                # objdict["xmax"]=xmax
                # objdict["confidence"]=scores[i]
#                 objarr.append(objdict)
#                 if objdict["object_name"] not in objdictionary:
#                     objdictionary[objdict["object_name"]] = objdict
#                 else:
                output.append(objdict)
        
        if connflag == True:
            rpiId = 1
            # obj = str(output)
            # paylodmsg0="{"
            # paylodmsg1="\"rpi_id\":"
            # paylodmsg2=",\"object\":\""
            # paylodmsg3="\"}"
            # paylodmsg = "{} {} {} {} {} {}".format(paylodmsg0, paylodmsg1, rpiId, paylodmsg2, obj, paylodmsg3)
            # paylodmsg = json.dumps(paylodmsg) 
            # paylodmsg_json = json.loads(paylodmsg)
            payloadmsg = {"rpi_id": rpiId ,"object": output}
            mqttc.publish("Object", json.dumps(payloadmsg), qos=1)   

        cv2.putText (frame,'Objects Detected : ' + str(count),(10,25),cv2.FONT_HERSHEY_SIMPLEX,1,(70,235,52),2,cv2.LINE_AA)
        cv2.imshow('Object Detector', frame)

        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()
print("Done")
