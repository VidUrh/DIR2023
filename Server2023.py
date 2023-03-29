import socket 
import threading
import time
from tkinter import *
import csv
import _thread
from gui import *






def handle_client(conn, addr):

    conn.close()


def start():
    print("[STARTING] server is starting...")
    server.listen()    
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")



if __name__ == '__main__':
    HEADER = 64
    PORT = 5050
    # Use reuseaddress
    
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = ('', PORT)
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!DISCONNECT"

    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server.bind(ADDR)   
    # Start the server thread
    
    thread = threading.Thread(target=start)
    thread.start()
    
    # Start the GUI thread
    start_GUI()
    
