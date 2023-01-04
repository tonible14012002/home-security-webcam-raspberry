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
