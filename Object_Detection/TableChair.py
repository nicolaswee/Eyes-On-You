import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    
import pathlib
import tensorflow as tf
import cv2
import argparse
from threading import Thread
import paho.mqtt.client as paho
import socket
import ssl
import string
import json
import time
import datetime
tf.get_logger().setLevel('ERROR')           
connflag = False
def on_connect(client, userdata, flags, rc):               
    global connflag
    connflag = True
 
def on_message(client, userdata, msg):                 
    print(msg.topic+" "+str(msg.payload))
    
mqttc = paho.Client()                                     
mqttc.on_connect = on_connect                           
mqttc.on_message = on_message
 #### 
awshost = "a177q8cgn9d0hx-ats.iot.ap-southeast-1.amazonaws.com"     
awsport = 8883                                            
clientId = "IoTProject_client"                                 
thingName = "IoTProject_client"                                 
caPath = "/home/pi/Downloads/AmazonRootCA1.pem"                                     
certPath = "/home/pi/Downloads/f6b9562445-certificate.pem.crt"                         
keyPath = "/home/pi/Downloads/f6b9562445-private.pem.key"                         
 
mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqttc.connect(awshost, awsport, keepalive=60)            
mqttc.loop_start()      
class VideoStream:
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
parser.add_argument('--model', help='Folder that the Saved Model is Located In',
                    default='od-models/tabletraymodel')
parser.add_argument('--labels', help='Where the Labelmap is Located',
                    default='od-models/tabletraymodel/label_map.pbtxt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                    default=0.7)
                    
args = parser.parse_args()
PATH_TO_MODEL_DIR = args.model
PATH_TO_LABELS = args.labels
MIN_CONF_THRESH = float(args.threshold)

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
PATH_TO_SAVED_MODEL = PATH_TO_MODEL_DIR + "/saved_model"
print('Loading model...', end='')
start_time = time.time()
detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
end_time = time.time()
elapsed_time = end_time - start_time
print('Done! Took {} seconds'.format(elapsed_time))
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')   
print('Running inference for PiCamera')
videostream = VideoStream(resolution=(640,480),framerate=30).start()
while True:
    frame = videostream.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame_expanded = np.expand_dims(frame_rgb, axis=0)
    imH, imW, _ = frame.shape
    input_tensor = tf.convert_to_tensor(frame)
    input_tensor = input_tensor[tf.newaxis, ...]
    detections = detect_fn(input_tensor)
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                   for key, value in detections.items()}
    detections['num_detections'] = num_detections
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
    scores = detections['detection_scores']
    boxes = detections['detection_boxes']
    classes = detections['detection_classes']
    output = []
    for i in range(len(scores)):
        if (scores[i] > MIN_CONF_THRESH):
            ymin = int(max(1,(boxes[i][0] * imH)))
            xmin = int(max(1,(boxes[i][1] * imW)))
            ymax = int(min(imH,(boxes[i][2] * imH)))
            xmax = int(min(imW,(boxes[i][3] * imW)))
            confidence = scores[i]
            cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
            object_name = category_index[int(classes[i])]['name'] 
            label = '%s: %d%%' % (object_name, int(scores[i]*100)) 
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) 
            label_ymin = max(ymin, labelSize[1] + 10) 
            cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) 
            cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) 
            objdict={}
            objdict["object_name"]=object_name
            objdict["ymin"]=ymin
            objdict["ymax"]=ymax
            objdict["xmin"]=xmin
            objdict["xmax"]=xmax
            objdict["confidence"]=confidence
            output.append(objdict)        
    if connflag == True:
        rpiId = 1
        obj = str(output)
        paylodmsg0="{"
        paylodmsg1="\"rpi_id\":"
        paylodmsg2=",\"object\":\""
        paylodmsg3="\"}"
        paylodmsg = "{} {} {} {} {} {}".format(paylodmsg0, paylodmsg1, rpiId, paylodmsg2, obj, paylodmsg3)
        paylodmsg = json.dumps(paylodmsg) 
        paylodmsg_json = json.loads(paylodmsg)       
        mqttc.publish("object_db", paylodmsg_json , qos=1)   
    cv2.imshow('Object Detector', frame)
    if cv2.waitKey(1) == ord('q'):
        break
cv2.destroyAllWindows()
print("Done")
