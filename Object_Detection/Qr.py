import os   
import pathlib
import cv2
import argparse
from threading import Thread
import paho.mqtt.client as paho
import socket
import ssl
import string
import json
import time
from pyzbar import pyzbar
import datetime      
connflag = False
def on_connect(client, userdata, flags, rc):             
    global connflag
    connflag = True
 
def on_message(client, userdata, msg):                     
    print(msg.topic+" "+str(msg.payload))
    
mqttc = paho.Client()                                    
mqttc.on_connect = on_connect                            
mqttc.on_message = on_message
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
print('Running inference for PiCamera')
videostream = VideoStream(resolution=(640,480),framerate=30).start()
bId1=""
bId2=""
while True:
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
            bId1 = barcodeData
        if connflag == True and bId2 != bId1:
            bId2 = barcodeData
            rpiId = 1
            QrName= barcodeData.split(",")
            qr_id = int(QrName[0])
            store_id= int(QrName[1]) 
            paylodmsg0="{"
            paylodmsg1="\"rpi_id\":"
            paylodmsg2=",\"qr_id\":\""
            paylodmsg3="\",\"store_id\":\""
            paylodmsg4="\"}"
            paylodmsg = "{} {} {} {} {} {} {} {}".format(paylodmsg0, paylodmsg1, rpiId, paylodmsg2, qr_id, paylodmsg3, store_id, paylodmsg4)
            paylodmsg = json.dumps(paylodmsg) 
            paylodmsg_json = json.loads(paylodmsg)       
            mqttc.publish("qr_db", paylodmsg_json , qos=1)   
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF

    if cv2.waitKey(1) == ord('q'):
        break
cv2.destroyAllWindows()
print("Done")
