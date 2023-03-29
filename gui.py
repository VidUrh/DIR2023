"""
Script responsible for the GUI of the application and for the server-side communication
"""
import tkinter as tk
from tkinter import simpledialog
from PIL import ImageTk, Image
import socket 
import threading
import cv2


class GUI:
    def __init__(self):
        self.server = None
        self.HEADER = 64
        self.PORT = 5050
        # Use reuseaddress
        self.QRcode = "300 323 002"

        self.SERVER = socket.gethostbyname(socket.gethostname())
        ADDR = ('', self.PORT)
        self.FORMAT = 'utf-8'
        
        
        self.win = tk.Tk()
        self.win.title("Pakiranje števcev")
        self.win.geometry("900x600+10+20")

        btn1 = tk.Button(self.win, text="START", font=("Arial", 12, "bold"), bg="yellow")
        btn1.place(x=50, y=50)
        #btn2 = tk.Button(self.win, text="STOP", font=("Arial", 12, "bold"), bg="red")
        #btn2.place(x=120, y=50)
        
        
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cap.set(5, 60)

        print(self.cap.get(5)) 

        '''
        stanja:
            skeniranje lokacije ovitka
            pobiranje ovitka
            razpiranje ovitka
            skeniranje lokacije števca
            pobiranje števca
            skeniranje QR kode
            vstavljanje števca v ovitek
            zapiranje vogalnih zapor
            odlaganja na paleto
            cikel zaključen
        '''
        #trenutnoStanje = "pobiranje kartona"
        trenutnoStanje = "skeniranje QR kode"
        stanje1 = tk.Label(self.win, text="stanje:", font=("Arial", 15))
        stanje1.place(relx=0.05, rely=0.2)
        self.stanje = tk.Label(self.win, text=trenutnoStanje, font=("Arial", 15), fg="gray")
        self.stanje.place(relx=0.13, rely=0.2)

        self.update_GUI(trenutnoStanje)

        paletizacija = tk.Label(self.win, text="paletizacija:", font=("Arial", 15))
        paletizacija.place(relx=0.05, rely=0.3)

        def izbiraPal():
            print(pal.get())
        
        def pal1():
            pal.set(1)
        def pal2():
            pal.set(2)
        def pal3():
            pal.set(3)

        pal = tk.IntVar()
        pal.set(0)
        pi1 = ImageTk.PhotoImage(Image.open("p1.png"))
        pi1b = tk.Button(self.win, image=pi1, command=pal1)
        pi1b.place(x=100, y=220)
        pi2 = ImageTk.PhotoImage(Image.open("p2.png"))
        pi2b = tk.Button(self.win, image=pi2, command=pal2)
        pi2b.place(x=250, y=220)
        pi3 = ImageTk.PhotoImage(Image.open("p3.png"))
        pi3b = tk.Button(self.win, image=pi3, command=pal3)
        pi3b.place(x=400, y=220)

        p1 = tk.Radiobutton(self.win, text="1", variable=pal, value=1, command=izbiraPal)
        p2 = tk.Radiobutton(self.win, text="2", variable=pal, value=2, command=izbiraPal)
        p3 = tk.Radiobutton(self.win, text="3", variable=pal, value=3, command=izbiraPal)
        p1.place(x=145, y=370)
        p2.place(x=295, y=370)
        p3.place(x=445, y=370)
        
    
        
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.server.bind(ADDR)   
        # Start the server thread
        
        thread = threading.Thread(target=self.start,daemon=True)
        thread.start()
        
        self.win.mainloop()
    
    def update_GUI(self, stanje):
        self.stanje.config(text=stanje)
        if (stanje == "skeniranje QR kode"):
            self.QRkoda = tk.Label(self.win, text="QR koda: ", font=("Arial", 15), fg="gray")
            self.QRkoda.place(relx=0.5, rely=0.2)
        elif (stanje == "vstavljanje števca v ovitek"):
            self.QRkoda = tk.Label(self.win, text="QR koda: "+self.QRcode, font=("Arial", 15), fg="gray")
            self.QRkoda.place(relx=0.5, rely=0.2)
        else:
            self.QRkoda.place_forget()   

    def handle_client(self, conn, addr):
        print("[NEW CONNECTION] {} connected.".format(addr))
        connected = True
        while connected:
            msg = conn.recv(self.HEADER).decode(self.FORMAT)        
            if msg.startswith("stanje"):
                print(msg[6:])
            self.update_GUI(msg)
        conn.close()
        
    def start(self):
        print("[STARTING] server is starting...")
        self.server.listen()    
        print(f"[LISTENING] Server is listening on {self.SERVER}")
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            
    def getQRCodeValue(self):
        _, frame = self.cap.read()
               
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(frame)

        # Draw rectangle around QR code on the frame
        if (points is not None):
            return value
            #300 323 001
            #300 323 002
            #300 323 003



if __name__ == "__main__":
    GUI()