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

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(ADDR)


    root=Tk()
    root.geometry("1000x750")
    
    # Start the server thread
    
    thread = threading.Thread(target=start)
    thread.start()
    
    # Start the GUI thread
    GUIthread = threading.Thread(target=start_GUI)
    GUIthread.start()
    
