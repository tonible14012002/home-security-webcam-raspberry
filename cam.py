from utils import db
import cv2
import threading
import face_recognition
import numpy as np

class Camera():

    def __init__(self) -> None:
        self.video = cv2.VideoCapture(0)
        self.grabbed, self.frame = self.video.read()
        img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.small_img = cv2.resize(img, (0,0), fx=0.25, fy=0.25)
        self.stopped = False

        self.small_face_locations = []
        # self.processing_face = False 
        self.recognized_names = []
        self.lock = threading.Lock()
        try:
            data = db.get_users()
            self.users = data['users']
            self.encodings = data['encodings']
        except Exception as e:
            self.users = []
            self.encodings = []
            print(e)

    def start(self):
        threading.Thread(target=self.update).start()
        return self

    def __del__(self):
        self.video.release()
    
    def update(self):
        while not self.stopped:
            self.grabbed, self.frame = self.video.read()
            if not self.grabbed:
                self.stop()
    
    def stop(self):
        self.stopped = True
    
    def read(self):
        return self.grabbed, self.frame

    # def detect_face(self):
    #     while not self.stopped:
    #         if self.processing_face:
    #             encodings = face_recognition.face_encodings(self.small_img, self.small_face_locations)
    #             for encoding in encodings:
    #                 user = db.detect_face(encoding, 0.5)
    #                 print(user)
                    
    def dectect(self):
        encodings = face_recognition.face_encodings(self.small_img, self.small_face_locations)
        for encoding in encodings:
            user = db.detect_face(encoding, 0.5)
            print(user)
            if user is not None:
                print('running')
                db.add_visit(user[0])
                
                self.recognized_names.append(f"{user[1]} {user[2]}")
                threading.Timer(5, self.show_name_timeout).start()
            else:
                self.recognized_names.append("Unknown")
                threading.Timer(5, self.show_name_timeout).start()

    def show_name_timeout(self):
        self.lock.acquire()
        if len(self.recognized_names):
            del self.recognized_names[0]
        self.lock.release()
                        
    # def start_detect(self):
    #     self.processing_face = True

    # def stop_detect(self):
    #     self.processing_face = False
    
    def find_face_location(self):
        small_img_bgr = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        
        self.small_img = cv2.resize(small_img_bgr, (0,0), fx=0.25, fy=0.25)
        self.small_face_locations = face_recognition.face_locations(self.small_img)
        
        return self.small_face_locations
    
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

        self.lock.acquire()
        for i in range(len(self.recognized_names)):
            name = self.recognized_names[i]
            cv2.putText(frame, name, (50, 30*i + 100), font, 1, (0,0,0), 1,)
        self.lock.release()

        ret, jpeg = cv2.imencode('.jpg', frame) 
        
        return jpeg.tobytes()