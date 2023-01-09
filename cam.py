from utils import db, http
import cv2
import threading
import face_recognition

class Camera():

    def __init__(self) -> None:

        # Create camera, get first frame
        self.video = cv2.VideoCapture(0)
        self.grabbed, self.frame = self.video.read()

        # small_img for face_recognition
        # resize to 1/4 to increase face detection speed
        img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.small_img = cv2.resize(img, (0,0), fx=0.25, fy=0.25)

        self.stopped = False

        # Location of faces in frames
        self.small_face_locations = []
        
        # Name of recognised users
        self.recognized_names = []

        # Mutex lock for multithread
        self.lock = threading.Lock()

        # 

    #

    def start(self):
        """
        Start capturing frames
        """
        threading.Thread(target=self.update).start()
        return self

    def __del__(self):
        # self.video.release()
        pass
    
    def update(self):
        """
        Run in another thread
        get latest frame from camera
        """
        while not self.stopped:
            self.grabbed, self.frame = self.video.read()
            if not self.grabbed:
                self.stop()
    
    def stop(self):
        """ Stop the camera """
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
        """
        Recognise face when button pressed
        """
        # get (128-dimensions) vector encodings of all faces on current frame 
        # use speedup encoding if face_location is known
        encodings = face_recognition.face_encodings(self.small_img, self.small_face_locations)
        # base on facelocation -> encodings: list
        
        # For each face encoding, compare to encoding in Database
        # Face is valid if the Euclien distance (threshold) is smaller than 0.5
        for encoding in encodings:
            # compare to faces in database
            # user = db.detect_face(encoding, 0.5)
            def on_response(response):
                if response.status_code >= 400:
                    self.show_recognized("Unknown")
                    return
                user = response.json()
                fullname = user['first_name'] + ' ' + user['last_name']
                self.show_recognized(fullname.strip())
                http.visit_alert(user['id'])

            http.detect(encoding, on_response)
            # if user is not None:
            #     print(user)
                # send server notification to add new visit and alert online admin
                # http.visit_alert(user[0]) # 

                # self.recognized_names.append(f"{user[1]} {user[2]}")
                # Set timeout for deleting Name shown on frame
                # threading.Timer(5, self.show_name_timeout).start()
            # else:
            #     self.show_recognized("Unknown")
        
    def show_recognized(self, name):
        self.recognized_names.append(name)
        threading.Timer(5, self.show_name_timeout).start()

    def show_name_timeout(self):
        """
        Delete name shown on screen when timeout 
        "FIFO"
        """
        self.lock.acquire()
        if len(self.recognized_names):
            del self.recognized_names[0]
        self.lock.release()
                        
    def find_face_location(self):
        """
        Find location of faces on current frame
        store it to small_face_locations (location in small img, not small face)

        """
        small_img_bgr = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.small_img = cv2.resize(small_img_bgr, (0,0), fx=0.25, fy=0.25)
        self.small_face_locations = face_recognition.face_locations(self.small_img)
        
        return self.small_face_locations
    
    def get_frame(self):
        """
        Will be called in a loop 
        get Current frame, display face location and recognised names
        convert frame to bytes type for streaming through HTTP
        """
        _, frame = self.read()

        # Find face location in the small frame (faster)
        face_locations = self.find_face_location()
        
        # convert face location in small frame to original size
        for (top, right, bottom, left) in face_locations:
            top*=4
            right*=4
            left*=4
            bottom*=4
            # draw rect on frame
            cv2.rectangle(frame, (left-20, top-10), (right+20, bottom+15), (300, 0, 0), 2)        
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL

        # show name detected
        self.lock.acquire()
        for i in range(len(self.recognized_names)):
            name = self.recognized_names[i]
            cv2.putText(frame, name, (50, 30*i + 100), font, 1, (0,0,0), 1,)
        self.lock.release()

        _, jpeg = cv2.imencode('.jpg', frame) 
        byte_buffer = jpeg.tobytes()

        return byte_buffer
    
