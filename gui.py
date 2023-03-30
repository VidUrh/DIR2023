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
import pickle
import time
import json

class GUI:
    def __init__(self):
        self.server = None
        self.HEADER = 64
        self.PORT = 5050
        # Use reuseaddress
        self.QRcode = ""
        self.mayIStart = False

        self.SERVER = socket.gethostbyname(socket.gethostname())
        ADDR = ('', self.PORT)
        self.FORMAT = 'utf-8'
        
        self.root = tk.Tk()
        self.root.title("Pakiranje števcev")
        self.root.geometry("900x630")
        
        bgImage = ImageTk.PhotoImage(Image.open("background.jpg"))
        self.win = tk.Label(self.root, image = bgImage)
        self.win.place(x = 0, y = 0)

        
        btn1 = tk.Button(self.win, text="START", font=("Arial", 12, "bold"), bg="green", command = lambda : self.switch_state(1))
        btn1.place(x=50, y=50)
        
        btn2 = tk.Button(self.win, text="STOP", font=("Arial", 12, "bold"), bg="red", command = lambda : self.switch_state(0))
        btn2.place(x=150, y=50)
        
        
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
        
        self.switch = tk.Label(self.win, bg="green", width=4, height=2)
        self.switch.place(x=750, y=50)

        self.update_GUI(trenutnoStanje)
        
        self.updateSwitch()

        paletizacija = tk.Label(self.win, text="paletizacija:", font=("Arial", 15))
        paletizacija.place(relx=0.05, rely=0.3)

        def izbiraPal():
            print(self.pal.get())
        
        def pal1():
            self.pal.set(1)
        def pal2():
            self.pal.set(2)
        def pal3():
            self.pal.set(3)

        
        
        self.pal = tk.IntVar(value=1)
        self.pal.set(1)
        pi1 = ImageTk.PhotoImage(Image.open("p1.png"))
        pi1b = tk.Button(self.win, image=pi1, command=pal1)
        pi1b.place(x=200, y=220)
        pi2 = ImageTk.PhotoImage(Image.open("p2.png"))
        pi2b = tk.Button(self.win, image=pi2, command=pal2)
        pi2b.place(x=350, y=220)
        pi3 = ImageTk.PhotoImage(Image.open("p3.png"))
        pi3b = tk.Button(self.win, image=pi3, command=pal3)
        pi3b.place(x=500, y=220)

        p1 = tk.Radiobutton(self.win, text="1", variable=self.pal, value=1, command=izbiraPal)
        p2 = tk.Radiobutton(self.win, text="2", variable=self.pal, value=2, command=izbiraPal)
        p3 = tk.Radiobutton(self.win, text="3", variable=self.pal, value=3, command=izbiraPal)
        p1.place(x=245, y=370)
        p2.place(x=395, y=370)
        p3.place(x=545, y=370)
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.server.bind(ADDR)   
        # Start the server thread
        
        
        with open("calibration.pkl", 'rb') as calibrationFile:
            data = pickle.load(calibrationFile)
            cameraMatrix = data['cameraMatrix']
            dist = data['dist']
            self.dist = dist
            self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(
                cameraMatrix, dist, (960, 540), 1, (960, 540))
        
        
        
        thread = threading.Thread(target=self.start,daemon=True)
        thread.start()
        
        self.root.mainloop()
    
    def switch_state(self, state):
        self.mayIStart = bool(state == 1)
        self.updateSwitch()
    
    def updateSwitch(self):
        if self.mayIStart:
            self.switch.config(bg="green")
        else:
            self.switch.config(bg="red")
    
    def resize_frame(self, frame):
        return cv2.resize(frame, (0, 0), fx=0.9, fy=0.9)
    
    def crop_frame(self, frame):
        return frame[20:380, 50:480]
    
    def update_GUI(self, stanje):
        self.stanje.config(text=stanje)
        if (stanje == "skeniranje QR kode"):
            self.QRkoda = tk.Label(self.win, text="QR koda: ", font=("Arial", 15), fg="gray")
            self.QRkoda.place(relx=0.5, rely=0.2)
        else:
            self.QRkoda.place_forget()
        
        if (self.QRkoda != ""):
            self.QRkoda = tk.Label(self.win, text="QR koda: "+self.QRcode, font=("Arial", 15), fg="gray")
            self.QRkoda.place(relx=0.5, rely=0.2)

    def handle_client(self, conn, addr):
        print("[NEW CONNECTION] {} connected.".format(addr))
        connected = True
        while connected:
            msg = conn.recv(self.HEADER).decode(self.FORMAT)        
            print(msg)
            if msg == "ScanQR":
                qrCodeValue = self.getQRCodeValue()
                if qrCodeValue is None:
                    qrCodeValue = 2
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
                print(stevecPos)
                if stevecPos is None:
                    conn.send(f"(-1)\n".encode(self.FORMAT))
                else:
                    x, y, orient = stevecPos
                    conn.send(f"({x}, {y}, {orient})\n".encode(self.FORMAT))
                    
            elif msg == "GetSkatlaPos":
                skatlaPOS = self.getSkatlaPos()
                print(skatlaPOS)
                if skatlaPOS is None:
                    conn.send(f"(1)\n".encode(self.FORMAT))
                else:
                    x, y, orient = skatlaPOS
                    conn.send(f"({x}, {y}, {orient})\n".encode(self.FORMAT))        
            elif msg == "mayIStart":
                conn.send(f"({self.mayIStart})\n".encode(self.FORMAT))  
            
            elif msg == "IsSkatlaOK":
                conn.send(f"({self.getSkatlaOk()})\n".encode(self.FORMAT))
                
            elif msg == "whichPal":
                conn.send(f"({self.pal.get()})\n".encode(self.FORMAT))
            
            else:
                self.update_GUI(msg)
                conn.send("Msg received".encode(self.FORMAT))
        
        conn.close()
    def getSkatlaOk(self):
        """Function for checking if the skatla is correctly erected
        """
        #ret, frame = self.cap.read()
        ret, frame = True, cv2.imread("skatlaNotOk.jpg")
        frame = self.calibrateImage(frame)
        frame = self.resize_frame(frame)
        
        minRGB = np.array([17, 41, 64])
        maxRGB = np.array([96, 141, 160])
        
        # Detect square stevec in frame
        if not ret:
            return "NO CAMERA"
        
        #frame = cv2.blur(frame, (7, 7))
        
        maskS = cv2.inRange(frame, minRGB, maxRGB)
        
        kernel = np.ones((3,3), np.uint8)
        maskS = cv2.erode(maskS, kernel, iterations=5)
        maskS = cv2.dilate(maskS, kernel, iterations=2)
        
        roi = maskS[400:, 750:]

        if roi[70,70] == 255:
            return 1
        else:
            return 0
        
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
        return "123 123 007"
        _, frame = self.cap.read()
        cv2.imwrite("qrKODASKEN.jpg",frame)
        #frame = cv2.imread("qrkoda.jpg")
        
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(frame)

        # Draw rectangle around QR code on the frame
        if (points is not None):
            return value
            #300 323 001
            #300 323 002
            #300 323 003
        return None

    def calibrateImage(self, frame):
        return cv2.undistort(frame, self.newcameramtx, self.dist, None, self.newcameramtx)

    def getStevecPos(self):
        ret, frame = self.cap.read()
        # ret, frame = True, cv2.imread("stevecIzPozKamZERO.jpg")
        frame = self.calibrateImage(frame)
        frame = self.resize_frame(frame)
        frame = self.crop_frame(frame)
        
        minHsvS = np.array([0, 0, 165])
        maxHsvS = np.array([360, 255, 250])

        # Detect square stevec in frame
        if not ret:
            return "NO CAMERA"
        
        
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.equalizeHist(frame)
        frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        
        cv2.blur(frame, (7, 7))
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        
        maskS = cv2.inRange(hsv, minHsvS, maxHsvS)
        
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

        x, y, orient = self.transformToFeatureSpace(rectCx, rectCy, -orientation, frame)
        return x/1000, y/1000, orient
    
    def transformToFeatureSpace(self, x, y, orient, frame = None):
        with open("originPoints.json", "r") as file:
            originPoints = json.load(file)
            origin = originPoints["origin"]
            coordX = originPoints["x"]
            pixelToMm = originPoints["pixelToMm"]
            originRotation = originPoints["originRotation"]
        if frame is not None:
            cv2.circle(frame, (int(x), int(y)), 5, (255, 0, 0), -1)
        x = (x - origin[0]) * pixelToMm
        y = (y - origin[1]) * pixelToMm
        
        # Rotate coordinates from camera frame to origin frame
        rotatedX = x * math.cos(originRotation) - y * math.sin(originRotation)
        rotatedY = x * math.sin(originRotation) + y * math.cos(originRotation)
        
        if frame is not None:
            cv2.circle(frame, (int(origin[0]), int(origin[1])), 5, (0, 255, 255), -1)
        cv2.imwrite("skatla.jpg", frame)
        
        return rotatedX, rotatedY, orient - originRotation
        
    def getSkatlaPos(self):
        ret, frame = self.cap.read()
        #ret, frame = True, cv2.imread("SkatlaLoc.jpg")
        frame = self.calibrateImage(frame)
        frame = self.resize_frame(frame)
        frame = self.crop_frame(frame)

        minHsvS = np.array([0, 0, 120])
        maxHsvS = np.array([360, 255, 250])

        # Detect square stevec in frame
        if not ret:
            return "NO CAMERA"
        
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.equalizeHist(frame)
        frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        
        cv2.blur(frame, (7, 7))
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        
        maskS = cv2.inRange(hsv, minHsvS, maxHsvS)
        
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
        cv2.putText(frame, str(-orientation), (int(rectCx), int(rectCy)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        x, y, orient = self.transformToFeatureSpace(rectCx, rectCy, -orientation, frame)
        return x/1000, y/1000, orient

if __name__ == "__main__":
    GUI()