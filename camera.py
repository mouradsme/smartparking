import cv2
import numpy as np
import easyocr
import multiprocessing as mp
import time
import serial
import sqlite3
from datetime import datetime

ser = serial.serial_for_url('rfc2217://localhost:4000', baudrate=115200)
def insert_history_record(plate_number, name, phone):
    conn = sqlite3.connect('history.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO history_table (plate_number, Name, Phone, timestamp) VALUES (?, ?, ?, ?)", (plate_number, name, phone, timestamp))
    conn.commit()
    conn.close()
def fetch_record_by_plate_number(plate_number):
    conn = sqlite3.connect('license_plates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM license_plates WHERE plate_number=?", (plate_number,))
    record = c.fetchall() 
    conn.close()
    return record

def detect_plate(populate_history):
    vid = cv2.VideoCapture(0)

    while True:
        ret, img = vid.read()
        
        if ret == True:
        
        
            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bfilter = cv2.bilateralFilter(gray, 11, 11, 17)
        edged = cv2.Canny(bfilter, 30, 200)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        location = None

        for contour in contours:
            approx = cv2.approxPolyDP(contour, 10, True)
            if len(approx) == 4:
                location = approx
                break

        if location is not None:

            mask = np.zeros(gray.shape, np.uint8)
            cv2.drawContours(mask, [location], 0, 255, -1)

            new_image = cv2.bitwise_and(img, img, mask=mask)

            (x, y) = np.where(mask == 255)
            (x1, y1) = (np.min(x), np.min(y))
            (x2, y2) = (np.max(x), np.max(y))
            cropped_image = gray[x1:x2+4, y1:y2+4]
            # Display the resulting frame
            cv2.rectangle(img, (y1, x1), (y2+4, x2+4), (0, 255, 0), 3)

            cv2.imshow('Frame',img)

            reader = easyocr.Reader(['en'])
            result = reader.readtext(cropped_image)
            if result:
                text = result[0][1]
                res = filter(lambda x: x.isalnum(), text)
                res = "".join(res)
                print(res)
                if (len(res) > 2):
                    Res = fetch_record_by_plate_number(res)
                    if (Res != None and len(Res) > 0):
                        type = Res[0][3]
                        Type = None
                        if (type == "Student"): 
                            Type = b'1'
                        
                        if (type == "Staff"): 
                            Type = b'2'
                        
                        if (type == "Teacher"): 
                            Type = b'3'
                        print('Found ', Type)
                        insert_history_record(Res[0][0], Res[0][1], Res[0][2])
                        populate_history()
                        ser.write(Type)

                        time.sleep(5) 