import requests
import threading

request = requests.sessions.Session()
base_url = 'http://127.0.0.1:8000'

def visit_alert(uid):
    def notify ():
        data = {
            'id': uid
        }
        url = base_url + '/camera/notify-visit/'
        try: 
            response = request.post(url, json=data)
            print(response)
        except Exception as e:
            print(e)
    
    threading.Thread(target=notify).start()

def detect(encoding, on_response):
    def call_detect():
        data = {
            'encoding': encoding.tolist()
        }
        url = base_url + '/camera/detect/'
        try:
            response = request.post(url, json=data)
            on_response(response)
        except Exception as e:
            print(e)
    
    threading.Thread(target=call_detect).start()