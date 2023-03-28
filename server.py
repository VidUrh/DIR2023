import socket 
import threading
import time
from tkinter import *
import csv
import _thread


HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = ('', PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)


root=Tk()
root.geometry("1000x750")

viale = []


def pretvori(pozicije):
    d = {x:i*12 for i,x in enumerate('ABCDEFGH')}
    for i,x in enumerate(pozicije):
        pozicije[i]=d[x[0]]+int(x[1:])
    print(pozicije)
    return sorted(pozicije)


def handle_client(conn, addr):
    print(f"Robot {addr} connected.")
    connected = True
    i=0
    posljiViale = False
    global viale
    while connected:
        msg = conn.recv(HEADER).decode(FORMAT)
        if msg=="zacni skeniranje":
            labelSkeniranje = Label(root,text="ZAČNI S SKENIRANJEM").grid(row=1,column=1)
            buttonNadaljuj = Button(root,text="NADALJUJ Z PROCESOM",command=lambda : nadaljujProces(conn)).grid(row=2,column=1)
        elif msg == 'Napaka':
            pass
        elif msg == 'Poslji indekse':
            while not len(viale):
                pass
            print(("("+str(len(viale))+")\n"))
            conn.send((f"({len(viale)})").encode())
            conn.send(('('+','.join(map(str,viale))+')\n').encode())
            viale=[]
        elif msg==DISCONNECT_MESSAGE:
            connected=False
            
    conn.close()


def nadaljujProces(conn):
    print("Zapri Label ZAČNI S SKENIRANJEM in shrani lokacije v bazo")
    conn.send(("(1)"+"\n").encode('utf-8'))
    print("Pošiljam: Skenirano\n")

def getVials(stAnaliza):
    scan = open('exportData.csv')
    database = open('SET1_csv.csv')

    databaseLines = [x.strip('\n').split(';') for x in database.readlines()[1:]]
    potrebneZaAnalizo = [x for x in databaseLines if x[6]=='Method_'+str(stAnaliza)]
    scanned = [x.strip('\n').split(',') for x in scan.readlines()]
    vials =[]

    potrebneKode = [a[0].strip() for a in potrebneZaAnalizo]
    
    for x in scanned:
        if x[1].strip() in potrebneKode:
            vials.append(x[0])

    return vials

    
def btn1Prit():
    global viale
    print(1)
    indexi = getVials(1)
    print(indexi)
    viale = pretvori(indexi)
    viale=[1,14,27,40,53]
    print(viale)
    
def btn2Prit():
    global viale
    print(2)
    indexi = getVials(2)
    print(indexi)
    viale = pretvori(indexi)
    print(viale)

def btn3Prit():
    global viale
    print(3)
    indexi = getVials(3)
    print(indexi)
    viale = pretvori(indexi)
    print(viale)

def btn4Prit():
    global viale
    print(4)
    indexi = getVials(4)
    print(indexi)
    viale = pretvori(indexi)
    print(viale)
    
def start():
    server.listen()    
    root=Tk()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


def start_GUI():
    label = Label(root,text="Izberi analizo").grid(row=0,column=1)
    btn1 = Button(root,text="Analiza 1",padx=5,pady=5,command=btn1Prit).grid(row=0,column=0)
    btn2 = Button(root,text="Analiza 2",padx=5,pady=5,command=btn2Prit).grid(row=1,column=0)
    btn3 = Button(root,text="Analiza 3",padx=5,pady=5,command=btn3Prit).grid(row=2,column=0)
    btn4 = Button(root,text="Analiza 4",padx=5,pady=5,command=btn4Prit).grid(row=3,column=0)
    _thread.start_new_thread(start, ())
    root.mainloop()

if __name__ == '__main__':
    print("[STARTING] server is starting...")
    start_GUI()
4
