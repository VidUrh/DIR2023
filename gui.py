"""
Script responsible for the GUI of the application and for the server-side communication
"""
import tkinter as tk
from tkinter import simpledialog
from PIL import ImageTk, Image
import socket 
import threading
import cv2
import numpy as np
import math
import datetime

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
            if msg == "ScanQR":
                qrCodeValue = self.getQRCodeValue()
                self.QRcode = qrCodeValue
                # Append the QR code value to the txt file
                with open("QRcodes.txt", "a") as file:
                    # write to file with timestamp
                    file.write(f"[QR SCAN] - {datetime.datetime.now()} - {qrCodeValue}\n")
                if qrCodeValue is not None and qrCodeValue != "":
                    conn.send(f"({int(self.QRcode.split(' ')[-1])})\n".encode(self.FORMAT))
                else:
                    conn.send(f"(-1)\n".encode(self.FORMAT))
            elif msg == "GetStevecPos":
                stevecPos = self.getStevecPos()
                if stevecPos is None:
                    conn.send(f"(-1)\n".encode(self.FORMAT))
                else:
                    x, y, orient = stevecPos
                    conn.send(f"({x}, {y}, {orient})\n".encode(self.FORMAT))
                    
            elif msg == "GetSkatlaPos":
                skatlaPOS = self.getSkatlaPos()
                if skatlaPOS is None:
                    conn.send(f"(-1)\n".encode(self.FORMAT))
                else:
                    x, y, orient = skatlaPOS
                    conn.send(f"({x}, {y}, {orient})\n".encode(self.FORMAT))
                    
                
            else:
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
        
        cv2.imshow("frame", frame)
        cv2.waitKey(0)
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(frame)

        # Draw rectangle around QR code on the frame
        if (points is not None):
            return value
            #300 323 001
            #300 323 002
            #300 323 003
        return None


    def getStevecPos(self):
        ret, frame = self.cap.read()
        #ret, frame = True, cv2.imread("stevecIzPozKam2.jpg")
        
        minHsvS = np.array([0, 0, 165])
        maxHsvS = np.array([360, 255, 250])

        # Detect square stevec in frame
        if not ret:
            return "NO CAMERA"
        
        #frame = frame[200:1300, 400:1500]
        frame = frame[50:400, 50:600]
        
        
        #frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.equalizeHist(frame)
        frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        
        cv2.blur(frame, (7, 7))
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        
        maskS = cv2.inRange(hsv, minHsvS, maxHsvS)
        cv2.imshow("Mask", maskS)
        
        kernel = np.ones((3,3), np.uint8)
        maskS = cv2.erode(maskS, kernel, iterations=5)
        maskS = cv2.dilate(maskS, kernel, iterations=2)
        
        contours, hierarchy = cv2.findContours(maskS, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        maxContour = None
        if (contours is not None and len(contours) > 0):
            minContourSize = 0
            maxContourSize = 1000000
            for i in contours:
                area = cv2.contourArea(i)
                if area > minContourSize and area < maxContourSize :
                    minContourSize = cv2.contourArea(i)
                    maxContour = i
                    
        if (maxContour is None):
            return None
                
        (x, y, w, h) = cv2.boundingRect(maxContour)
        
        x0 = int(x+w/2)
        y0 = int(y+h/2)
        r = int(h/2)
        if maskS[y0][x0] != 0:
            cv2.rectangle(frame, (x,y),(x+w,y+h), (255, 255, 255), 2)
        
        rotatedRect = cv2.minAreaRect(maxContour)
        box = cv2.boxPoints(rotatedRect)
        box = np.intp(box)

        # orientation is stored in the last element of the tuple returned by minAreaRect
        orientation = rotatedRect[-1]
        # Round orientation to 2 decimal places
        orientation = round(orientation, 2)

        # get width and height from rotated rectangle (first element is width, second is height)
        width, height = rotatedRect[-2]
        # Get orientation of the nozzle (if width is smaller than height, the nozzle is rotated 90 degrees)
        if width > height:
            orientation = orientation - 90

        rectCx, rectCy = rotatedRect[0] # Center of the rectangle
        cv2.circle(frame, (int(rectCx), int(rectCy)), 5, (255, 255, 255), -1)  # Draw center of the rectangle
        
        # Draw rotated rectangle
        cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
        cv2.putText(frame, str(orientation), (int(rectCx), int(rectCy)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imshow("Image", frame)
        cv2.waitKey(0)
        return rectCx, rectCy, orientation
    
    def getSkatlaPos(self):
        ret, frame = self.cap.read()
        #ret, frame = True, cv2.imread("skatla.jpg")
        
        minHsvS = np.array([0, 0, 150])
        maxHsvS = np.array([360, 255, 250])

        # Detect square stevec in frame
        if not ret:
            return "NO CAMERA"
        
        #frame = frame[200:1300, 400:1500]
        frame = frame[50:400, 50:600]
        
        
        #frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.equalizeHist(frame)
        frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        
        cv2.blur(frame, (7, 7))
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        
        maskS = cv2.inRange(hsv, minHsvS, maxHsvS)
        cv2.imshow("Mask", maskS)
        
        kernel = np.ones((3,3), np.uint8)
        maskS = cv2.erode(maskS, kernel, iterations=5)
        maskS = cv2.dilate(maskS, kernel, iterations=2)
        
        contours, hierarchy = cv2.findContours(maskS, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        maxContour = None
        if (contours is not None and len(contours) > 0):
            minContourSize = 0
            maxContourSize = 1000000
            for i in contours:
                area = cv2.contourArea(i)
                if area > minContourSize and area < maxContourSize :
                    minContourSize = cv2.contourArea(i)
                    maxContour = i
                    
        if (maxContour is None):
            return None
                
        (x, y, w, h) = cv2.boundingRect(maxContour)
        
        x0 = int(x+w/2)
        y0 = int(y+h/2)
        r = int(h/2)
        if maskS[y0][x0] != 0:
            cv2.rectangle(frame, (x,y),(x+w,y+h), (255, 255, 255), 2)
        
        rotatedRect = cv2.minAreaRect(maxContour)
        box = cv2.boxPoints(rotatedRect)
        box = np.intp(box)

        # orientation is stored in the last element of the tuple returned by minAreaRect
        orientation = rotatedRect[-1]
        # Round orientation to 2 decimal places
        orientation = round(orientation, 2)

        # get width and height from rotated rectangle (first element is width, second is height)
        width, height = rotatedRect[-2]
        # Get orientation of the nozzle (if width is smaller than height, the nozzle is rotated 90 degrees)
        if width > height:
            orientation = orientation - 90

        rectCx, rectCy = rotatedRect[0] # Center of the rectangle
    
        cv2.circle(frame, (int(rectCx), int(rectCy)), 5, (255, 255, 255), -1)      
        
        
        # Draw rotated rectangle
        cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
        cv2.putText(frame, str(orientation), (int(rectCx), int(rectCy)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imshow("Image", frame)
        cv2.imwrite("skatla.jpg", frame)
        cv2.waitKey(0)
        return rectCx, rectCy, orientation

if __name__ == "__main__":
    GUI()