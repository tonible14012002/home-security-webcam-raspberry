import numpy as np
import face_recognition
import cv2
import time
import threading
import os
from db import MyDB

class VideoStream:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        
        self.grabbed, self.frame = self.video.read()
        small_img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        
        self.small_img = cv2.resize(small_img, (0,0), fx=0.25, fy=0.25)

        self.stopped = False
        self.small_face_locations = []
        self.processing_face = False
        self.recognized_names = []
        
        self.db = MyDB(
            dbname='security',
            user='postgres',
            password='71102Tony',
            host='localhost',
            port='5433'
        )

        self.users_info = self.db.get_user_data_from_db()

    def start(self):
        self.update_thread = threading.Thread(target=self.update, args=()).start()
        self.detect_face_thread = threading.Thread(target=self.detect_faces, args=()).start()
        return self
  
    def __del__(self):
        self.video.release()
        del self.update_thread
        del self.detect_face_thread
        del self.db

    def detect_faces(self):
        while not self.stopped:
            if self.processing_face:
                encodings = face_recognition.face_encodings(self.small_img, self.small_face_locations)
                for encoding in encodings:
                    face_distances = face_recognition.face_distance(self.users_info['encodings'], encoding)
                    best_match_index = np.argmin(face_distances)
                    if face_distances[best_match_index] < 0.5:
                        self.add_recognized_names(self.users_info['names'][best_match_index])
                    else: 
                        self.add_recognized_names('Unknown')
                time.sleep(2)

    def add_recognized_names(self, name):
        self.recognized_names.append(name)
        threading.Timer(8,self.delete_recognised_name).start()
    
    def delete_recognised_name(self):
        try:
            print('deleting')
            del self.recognized_names[0]
        except:
            pass

    def find_face_location(self):
        small_img_bgr = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.small_img = cv2.resize(small_img_bgr, (0,0), fx=0.25, fy=0.25)

        self.small_face_locations = face_recognition.face_locations(self.small_img)
    
        self.processing_face = not self.processing_face    
        return self.small_face_locations
    
    def update(self):
        while not self.stopped:
            self.grabbed, self.frame = self.video.read()
            if not self.grabbed:
                self.stop()

    def stop(self):
        self.stopped=True
    
    def read(self):
        return self.grabbed, self.frame

    def get_frame(self):
        grabbed, frame = self.read()
        if not grabbed:
            return
        face_locations = self.find_face_location()

        for (top, right, bottom, left) in face_locations:
            top*=4
            right*=4
            left*=4
            bottom*=4
            cv2.rectangle(frame, (left-20, top-10), (right+20, bottom+15), (300, 0, 0), 2)        
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        try:
            for i in range(len(self.recognized_names)):
                name = self.recognized_names[i]
                cv2.putText(frame, name, (50, 30*i), font, 1, (0,0,0), 1)
        except:
            pass
        ret, jpeg = cv2.imencode('.jpg', frame) 

        return jpeg.tobytes()