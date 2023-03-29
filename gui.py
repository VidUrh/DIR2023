import tkinter as tk
from tkinter import simpledialog
from PIL import ImageTk, Image

def start_GUI():
    win = tk.Tk()
    win.title("Pakiranje števcev")
    win.geometry("900x600+10+20")
    canvas = tk.Canvas(win, width=900, height=600)
    canvas.pack()

    btn1 = tk.Button(win, text="START", font=("Arial", 12, "bold"), bg="yellow")
    btn1.place(x=50, y=50)
    #btn2 = tk.Button(win, text="STOP", font=("Arial", 12, "bold"), bg="red")
    #btn2.place(x=120, y=50)

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
    stanje1 = tk.Label(win, text="stanje:", font=("Arial", 15))
    stanje1.place(relx=0.05, rely=0.2)
    stanje2 = tk.Label(win, text=trenutnoStanje, font=("Arial", 15), fg="gray")
    stanje2.place(relx=0.13, rely=0.2)

    if (trenutnoStanje == "skeniranje QR kode" or trenutnoStanje == "vstavljanje števca v ovitek"):
        code = "300 323 002"
        QRkoda = tk.Label(win, text="QR koda: "+code, font=("Arial", 15), fg="gray")
        QRkoda.place(relx=0.5, rely=0.2)

    paletizacija = tk.Label(win, text="paletizacija:", font=("Arial", 15))
    paletizacija.place(relx=0.05, rely=0.3)

    def izbiraPal():
        print(pal)

    pi1 = ImageTk.PhotoImage(Image.open("p1.png"))
    pi1l = tk.Label(win, image=pi1)
    pi1l.place(x=100, y=220)
    pi2 = ImageTk.PhotoImage(Image.open("p2.png"))
    pi2l = tk.Label(win, image=pi2)
    pi2l.place(x=250, y=220)
    pi3 = ImageTk.PhotoImage(Image.open("p3.png"))
    pi3l = tk.Label(win, image=pi3)
    pi3l.place(x=400, y=220)

    pal = tk.IntVar()
    pal.set(0)
    p1 = tk.Radiobutton(win, text="1", variable=pal, value=1, command=izbiraPal)
    p2 = tk.Radiobutton(win, text="2", variable=pal, value=2, command=izbiraPal)
    p3 = tk.Radiobutton(win, text="3", variable=pal, value=3, command=izbiraPal)
    p1.place(x=145, y=370)
    p2.place(x=295, y=370)
    p3.place(x=445, y=370)

    win.mainloop()


if __name__ == "__main__":
    start_GUI()