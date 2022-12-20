from flask import Flask, Response, request, render_template
from cam import Camera
from flask_cors import CORS
import requests
import keyboard

app = Flask(__name__)
cors = CORS(app, resources={r"/": {"origins": "*"}})

# camera = VideoStream().start()
camera = Camera().start()

def gen():
    while True:
        try:
            if keyboard.is_pressed('d'):
                camera.dectect()
            print('event listenning \n')
        except Exception as e:
            print(e)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + camera.get_frame() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    # tokken = request.headers.get('Authorization', None)
    # if not tokken:
    #     return {'status': 'error'}
    # resp = requests.get('http://127.0.0.1:8000/accounts/verify/', headers={'Authorization': tokken})
    # if resp.status_code not in range(200, 300):
        return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    # return {
    #     "detail": "you are not allow"
    # }
    
# @app.route('/')
# def home():
#     tokken = request.headers.get('Authorization', None)
#     if not tokken:
#         return {'status': 'error'}
#     resp = requests.get('http://127.0.0.1:8000/accounts/verify/', headers={'Authorization': tokken})
#     if resp.status_code not in range(200, 300):
#         return {'status': 'error'}
#     return {
#         'status': 'success',
#         'html': render_template('index.html')
#     }
  
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False , threaded=True)
    