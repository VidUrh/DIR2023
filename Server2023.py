import socket 
import threading
import time
from tkinter import *
import csv
import _thread
from gui import *


HEADER = 64
PORT = 5050
# Use reuseaddress

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = ('', PORT)
FORMAT = 'utf-8'

GUIObj = None

def handle_client(conn, addr):
    global GUIObj
    connected = True
    while connected:
        msg = conn.recv(HEADER).decode(FORMAT)        
        if msg == "test":
            print("tst")
        if msg.startswith("stanje"):
            print(msg[6:])
            GUIObj.update_GUI(msg[6:])
            
    conn.close()


def start():
    print("[STARTING] server is starting...")
    server.listen()    
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")



if __name__ == '__main__':


    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server.bind(ADDR)   
    # Start the server thread
    
    thread = threading.Thread(target=start,daemon=True)
    thread.start()
    
    # Start the GUI thread
    GUIObj = GUI() 
    
