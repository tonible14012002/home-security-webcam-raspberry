import cv2, socket
import numpy as np
import base64
import pickle
import math

BUFF_SIZE = 65000

server_host = '10.130.108.210'
server_port = 9999
server_address = (server_host, server_port)

def start_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_bytes(sock, buffer: bytes):
    buffer_size = len(buffer)
    num_of_packs = 1
    if buffer_size > BUFF_SIZE:
        num_of_packs = math.ceil(buffer_size/BUFF_SIZE)
    
    frame_info = {'packs': num_of_packs}

    print('number of packs', num_of_packs)
    sock.sendto(pickle.dumps(frame_info), server_address)

    left = 0
    right = BUFF_SIZE

    for i in range(num_of_packs):
        print('left:', left)
        print('right', right)
        data = buffer[left:right]
        left = right
        right += BUFF_SIZE

        sock.sendto(data, server_address)